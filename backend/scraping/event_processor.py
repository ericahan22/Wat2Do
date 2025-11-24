import asyncio
import os
import sys

# Set up Django
if "django" not in sys.modules:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()

from asgiref.sync import sync_to_async
from django.utils import timezone

from apps.clubs.models import Clubs
from apps.events.models import Events
from scraping.logging_config import logger
from services.storage_service import upload_image_from_url
from utils.date_utils import parse_utc_datetime
from utils.scraping_utils import insert_event_to_db, append_event_to_csv


def _get_all_images(post):
    """
    Returns all image URLs for a post.
    """
    images = post.get("images", [])
    # Fallback to displayUrl if images missing
    if not images and post.get("displayUrl"):
        images = [post["displayUrl"]]
    return images

class EventProcessor:
    def __init__(self, concurrency=5):
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)

    @sync_to_async(thread_sensitive=True)
    def _get_club_type(self, ig_handle):
        try:
            return Clubs.objects.get(ig=ig_handle).club_type
        except Clubs.DoesNotExist:
            return None

    @sync_to_async(thread_sensitive=True)
    def _get_seen_shortcodes(self):
        """Fetch existing shortcodes to avoid processing duplicates."""
        try:
            # Get shortcodes only from successful events
            events = Events.objects.filter(source_url__contains="/p/").values_list("source_url", flat=True)
            event_codes = {url.strip("/").split("/")[-1] for url in events}
            return event_codes
        except Exception as e:
            logger.error(f"Error fetching seen shortcodes: {e}")
            return set()

    # --- Async Wrappers ---
    @sync_to_async(thread_sensitive=False)
    def _upload_image(self, url):
        return upload_image_from_url(url)

    @sync_to_async(thread_sensitive=False)
    def _extract_events(self, caption, all_s3_urls, post_time):
        from services.openai_service import extract_events_from_caption
        return extract_events_from_caption(
            caption_text=caption,
            all_s3_urls=all_s3_urls,
            post_created_at=post_time,
            source_image_url=None 
        )

    @sync_to_async(thread_sensitive=True)
    def _save_event(self, event_data, ig_handle, source_url, club_type):
        return insert_event_to_db(event_data, ig_handle, source_url, club_type)

    async def _process_single_post_extraction(self, post):
        """Extracts event data from a single post using OpenAI."""
        async with self.semaphore:
            timestamp_str = post.get("timestamp")
            post_dt = parse_utc_datetime(timestamp_str)

            return await self._extract_events(
                post.get("caption"),
                post.get("all_s3_urls"),
                post_dt
            )

    async def process(self, posts_data, cutoff_date):
        logger.info(f"Processing {len(posts_data)} posts...")

        seen_shortcodes = await self._get_seen_shortcodes()
        valid_posts = []

        # 1. Filter Posts
        for post in posts_data:
            url = post.get("url")
            ig_handle = post.get("ownerUsername") or "UNKNOWN"
            shortcode = url.strip("/").split("/")[-1] if url else "UNKNOWN"

            if not url or "/p/" not in url:
                logger.info(f"[{ig_handle}] Skipping: Invalid URL format ({url})")
                continue

            post_dt = parse_utc_datetime(post.get("timestamp"))
            if not post_dt or post_dt < cutoff_date:
                append_event_to_csv(post, ig_handle, url, added_to_db="old_post")
                logger.info(f"[{ig_handle}] [{shortcode}] Skipping: Post date {post_dt} is older than cutoff {cutoff_date}")
                continue

            if shortcode in seen_shortcodes:
                try:
                    event = await sync_to_async(Events.objects.get)(source_url=url)
                    event_name = event.title
                except Exception:
                    event_name = "UNKNOWN"
                append_event_to_csv(post, ig_handle, url, added_to_db="duplicate_post")
                logger.info(f"[{ig_handle}] [{shortcode}] Skipping: Event '{event_name}' already exists in DB")
                continue

            valid_posts.append(post)
            
        if not valid_posts:
            logger.info("No new valid posts found.")
            return 0

        logger.info(f"Found {len(valid_posts)} new posts. Starting image uploads...")

        # 2. Upload all images for each post (with carousel support)
        all_image_tasks = []
        for post in valid_posts:
            ig_handle = post.get("ownerUsername")
            shortcode = post.get("url", "").strip("/").split("/")[-1]
            logger.info(f"[{ig_handle}] [{shortcode}] Uploading images...")
            image_urls = _get_all_images(post)
            post["all_image_urls"] = image_urls
            all_image_tasks.append([self._upload_image(img_url) for img_url in image_urls])
        
        flat_tasks = [task for sublist in all_image_tasks for task in sublist]
        flat_results = await asyncio.gather(*flat_tasks, return_exceptions=True)
        for i, res in enumerate(flat_results):
            if isinstance(res, Exception):
                logger.error(f"Image upload failed: {res}")
                flat_results[i] = None
        
        # Map uploaded S3 URLs back to posts
        idx = 0
        for post in valid_posts:
            n_imgs = len(post["all_image_urls"])
            # Filter out failed uploads
            post["all_s3_urls"] = [url for url in flat_results[idx:idx + n_imgs] if url]
            idx += n_imgs

        # 3. Extract Events
        extract_tasks = []
        for post in valid_posts:
            ig_handle = post.get("ownerUsername")
            shortcode = post.get("url", "").strip("/").split("/")[-1]
            logger.info(f"[{ig_handle}] [{shortcode}] Extracting event data...")
            extract_tasks.append(self._process_single_post_extraction({
                **post,
                "all_s3_urls": post["all_s3_urls"]
            }))
        results = await asyncio.gather(*extract_tasks)

        # 4. Save to DB
        saved_count = 0
        for post, extracted_events in zip(valid_posts, results, strict=False):
            ig_handle = post.get("ownerUsername")
            source_url = post.get("url")
            shortcode = source_url.strip("/").split("/")[-1]
            all_s3_urls = post.get("all_s3_urls", [])

            if not extracted_events:
                logger.info(f"[{ig_handle}] [{shortcode}] No events found in post, skipping")
                continue

            if not isinstance(extracted_events, list):
                extracted_events = [extracted_events]

            # If 1 image is provided, but AI returned multiple event objects,
            # merge them into a single "Weekly/Summary" event.
            if len(all_s3_urls) == 1 and len(extracted_events) > 1:
                base_event = extracted_events[0]
                
                # 1. Consolidate all dates from all events into the first event
                combined_occurrences = []
                for evt in extracted_events:
                    combined_occurrences.extend(evt.get("occurrences") or [])
                base_event["occurrences"] = combined_occurrences
                
                # 2. Update title/description to reflect it's a summary
                club_name = post.get("ownerFullName") or ig_handle or "Club"
                base_event["title"] = f"{club_name} Weekly Events"
                base_event["description"] = (base_event.get("description") or "") + "\n\n(Condensed from multiple events)"
                
                extracted_events = [base_event]
                
            for event_data in extracted_events:
                # Map correct picture to event
                image_idx = event_data.get("image_index")
                if image_idx is not None and isinstance(image_idx, int) and 0 <= image_idx < len(all_s3_urls):
                    event_data["source_image_url"] = all_s3_urls[image_idx]
                else:
                    # Fallback: Use first image
                    event_data["source_image_url"] = all_s3_urls[0] if all_s3_urls else ""

                # Check for past date
                occurrences = event_data.get("occurrences", [])
                if occurrences:
                    first_occurrence = occurrences[0]
                    dtstart_utc = parse_utc_datetime(first_occurrence.get("dtstart_utc"))
                    if dtstart_utc and dtstart_utc < timezone.now():
                        append_event_to_csv(event_data, ig_handle, source_url, added_to_db="event_past_date")
                        logger.info(f"[{ig_handle}] [{shortcode}] Skipping event '{event_data.get('title')}' - event date {dtstart_utc} is in the past")
                        continue

                club_type = await self._get_club_type(ig_handle)
                try:
                    success = await self._save_event(event_data, ig_handle, source_url, club_type)
                except Exception as e:
                    append_event_to_csv(event_data, ig_handle, source_url, added_to_db="error", club_type=club_type)
                    logger.error(f"[{ig_handle}] [{shortcode}] Error saving event: {e}")
                    continue
                if success:
                    append_event_to_csv(event_data, ig_handle, source_url, added_to_db="success", club_type=club_type)
                    logger.info(f"[{ig_handle}] [{shortcode}] Saved event: '{event_data.get('title', '')}'")
                    saved_count += 1

        logger.info(f"Processing complete. Saved {saved_count} new events.")
        return saved_count
