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
import re

from apps.clubs.models import Clubs
from apps.events.models import Events
from scraping.logging_config import logger
from services.storage_service import upload_image_from_url
from services.openai_service import extract_events_from_caption
from utils.date_utils import parse_utc_datetime
from utils.scraping_utils import append_event_to_csv, insert_event_to_db


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
    def __init__(
        self,
        concurrency=5,
        school="University of Waterloo",
        dry_run=False,
    ):
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)
        self.school = school
        # When True, skip all DB writes (Events, EventDates). Reads still happen
        # so duplicate-shortcode filtering and club-type lookups work normally.
        self.dry_run = bool(dry_run)

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
            events = Events.objects.filter(source_url__contains="/p/").values_list(
                "source_url", flat=True
            )
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
            source_image_url=None,
            school=self.school,
        )

    @sync_to_async(thread_sensitive=True)
    def _save_event(self, event_data):
        """Save event to database. event_data should contain all metadata."""
        return insert_event_to_db(event_data)

    async def _extract_post_events(self, post):
        """Extract event data from a single post using OpenAI.

        All carousel images are passed as image blocks in one request; the
        prompt asks for an array of unique events back.
        """
        async with self.semaphore:
            post_dt = parse_utc_datetime(post.get("timestamp"))
            return await self._extract_events(
                post.get("caption"), post.get("all_s3_urls"), post_dt
            )

    async def process(self, posts_data, cutoff_date, scrape_runs=None):
        logger.info(f"Processing {len(posts_data)} posts...")

        # In dry-run, we want every post to flow through to AI extraction so we
        # can eyeball LLM output, even for posts already in DB.
        seen_shortcodes = set() if self.dry_run else await self._get_seen_shortcodes()
        valid_posts = []

        # 1. Filter Posts
        for post in posts_data:
            url = post.get("url")
            ig_handle = post.get("ownerUsername") or "UNKNOWN"
            shortcode = url.strip("/").split("/")[-1] if url else "UNKNOWN"

            logger.info(f"[{ig_handle}] [{shortcode}] Processing Instagram post...")

            if not url or "/p/" not in url:
                logger.info(f"[{ig_handle}] Skipping: Invalid URL format ({url})")
                continue

            post_dt = parse_utc_datetime(post.get("timestamp"))
            if not post_dt or post_dt < cutoff_date:
                # Create minimal event_data for logging
                log_data = {"ig_handle": ig_handle, "source_url": url, "posted_at": post_dt}
                append_event_to_csv(log_data, added_to_db="old_post")
                logger.info(
                    f"[{ig_handle}] [{shortcode}] Skipping: Post date {post_dt} is older than cutoff {cutoff_date}"
                )
                continue

            if shortcode in seen_shortcodes:
                try:
                    event = await sync_to_async(Events.objects.get)(source_url=url)
                    event_name = event.title
                except Exception:
                    event_name = "UNKNOWN"
                # Create minimal event_data for logging
                log_data = {"ig_handle": ig_handle, "source_url": url}
                append_event_to_csv(log_data, added_to_db="duplicate_post")
                logger.info(
                    f"[{ig_handle}] [{shortcode}] Skipping: Event '{event_name}' already exists in DB"
                )
                continue

            valid_posts.append(post)

        # Update posts_new on ScrapeRun
        if scrape_runs:
            for post in valid_posts:
                run = scrape_runs.get(post.get("ownerUsername"))
                if run:
                    run.posts_new += 1
            for run in scrape_runs.values():
                try:
                    await sync_to_async(run.save)(update_fields=["posts_new"])
                except Exception:
                    pass

        if not valid_posts:
            logger.info("No new valid posts found.")
            return 0

        logger.info(f"Found {len(valid_posts)} new posts. Starting image uploads...")

        # 2. Upload all images for each post (with carousel support)
        all_image_tasks = []

        async def _upload_image_bounded(url):
            async with self.semaphore:
                return await self._upload_image(url)

        for post in valid_posts:
            ig_handle = post.get("ownerUsername")
            shortcode = post.get("url", "").strip("/").split("/")[-1]
            logger.info(f"[{ig_handle}] [{shortcode}] Uploading images...")
            image_urls = _get_all_images(post)
            post["all_image_urls"] = image_urls
            all_image_tasks.append(
                [_upload_image_bounded(img_url) for img_url in image_urls]
            )

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
            post["all_s3_urls"] = [
                url for url in flat_results[idx : idx + n_imgs] if url
            ]
            idx += n_imgs

        # 3. Extract Events
        extract_tasks = []
        for post in valid_posts:
            ig_handle = post.get("ownerUsername")
            shortcode = post.get("url", "").strip("/").split("/")[-1]
            logger.info(f"[{ig_handle}] [{shortcode}] Extracting event data...")
            extract_tasks.append(self._extract_post_events(post))
        results = await asyncio.gather(*extract_tasks)

        # 4. Save to DB
        saved_count = 0
        for post, extracted_events in zip(valid_posts, results, strict=False):
            ig_handle = post.get("ownerUsername")
            source_url = post.get("url")
            shortcode = source_url.strip("/").split("/")[-1]
            all_s3_urls = post.get("all_s3_urls", [])

            if not extracted_events:
                logger.info(
                    f"[{ig_handle}] [{shortcode}] No events found in post, skipping"
                )
                continue

            if scrape_runs:
                run = scrape_runs.get(ig_handle)
                if run:
                    run.events_extracted += len(extracted_events) if isinstance(extracted_events, list) else 1
                    try:
                        await sync_to_async(run.save)(update_fields=["events_extracted"])
                    except Exception:
                        pass

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
                base_event["description"] = (
                    base_event.get("description") or ""
                ) + "\n\n(Condensed from multiple events)"

                extracted_events = [base_event]

            for event_data in extracted_events:
                # Map correct picture to event
                image_idx = event_data.get("image_index")
                if (
                    image_idx is not None
                    and isinstance(image_idx, int)
                    and 0 <= image_idx < len(all_s3_urls)
                ):
                    event_data["source_image_url"] = all_s3_urls[image_idx]
                else:
                    # Fallback: Use first image
                    event_data["source_image_url"] = (
                        all_s3_urls[0] if all_s3_urls else ""
                    )

                # Set identifying metadata before any CSV write so every row has handle/source/etc.
                event_data["ig_handle"] = ig_handle
                event_data["source_url"] = source_url
                event_data["school"] = self.school
                event_data["posted_at"] = post_dt
                event_data["likes_count"] = post.get("likesCount") or post.get("likeCount") or 0
                event_data["comments_count"] = post.get("commentsCount") or post.get("commentCount") or 0

                # Check for past date
                occurrences = event_data.get("occurrences", [])
                if occurrences:
                    first_occurrence = occurrences[0]
                    dtstart_utc = parse_utc_datetime(
                        first_occurrence.get("dtstart_utc")
                    )
                    if dtstart_utc and dtstart_utc < timezone.now():
                        append_event_to_csv(event_data, added_to_db="event_past_date")
                        logger.info(
                            f"[{ig_handle}] [{shortcode}] Skipping event '{event_data.get('title')}' - event date {dtstart_utc} is in the past"
                        )
                        continue

                event_data["club_type"] = await self._get_club_type(ig_handle)

                if self.dry_run:
                    append_event_to_csv(event_data, added_to_db="dry_run")
                    logger.info(
                        f"[{ig_handle}] [{shortcode}] [DRY-RUN] Would save event: '{event_data.get('title', '')}'"
                    )
                    saved_count += 1
                    continue

                try:
                    result = await self._save_event(event_data)
                except Exception as e:
                    append_event_to_csv(event_data, added_to_db="error")
                    logger.error(f"[{ig_handle}] [{shortcode}] Error saving event: {e}")
                    continue

                if result is True:
                    append_event_to_csv(event_data, added_to_db="success")
                    logger.info(
                        f"[{ig_handle}] [{shortcode}] Saved event: '{event_data.get('title', '')}'"
                    )
                    saved_count += 1
                    if scrape_runs:
                        run = scrape_runs.get(ig_handle)
                        if run:
                            run.events_saved += 1
                            try:
                                await sync_to_async(run.save)(update_fields=["events_saved"])
                            except Exception:
                                pass
                elif result == "updated":
                    append_event_to_csv(event_data, added_to_db="updated")
                    logger.info(
                        f"[{ig_handle}] [{shortcode}] Updated event: '{event_data.get('title', '')}'"
                    )
                    saved_count += 1
                    if scrape_runs:
                        run = scrape_runs.get(ig_handle)
                        if run:
                            run.events_saved += 1
                            try:
                                await sync_to_async(run.save)(update_fields=["events_saved"])
                            except Exception:
                                pass
                elif result == "duplicate":
                    append_event_to_csv(event_data, added_to_db="duplicate_post")
                    logger.info(
                        f"[{ig_handle}] [{shortcode}] Duplicate event (no changes): '{event_data.get('title', '')}'"
                    )

        logger.info(f"Processing complete. Saved {saved_count} new events.")
        return saved_count


def process_discord_message(data):
    """
    Core pipeline to process a Discord event message.
    Extracts events using OpenAI, fuzzy-matches the author, uploads attachments,
    and inserts the events into the database.
    """
    content = data.get("content")
    author_name = data.get("author_name")
    message_id = data.get("message_id")
    
    guild_id = data.get("guild_id", "0")
    channel_id = data.get("channel_id", "0")
    
    # Build unique Discord message URL
    source_url = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
    
    # Deduplicate early
    if Events.objects.filter(source_url=source_url).exists():
        logger.info(f"[Discord] [{message_id}] Skipping duplicate event for message URL: {source_url}")
        return {
            "status": "duplicate",
            "message": "Event with this message ID already exists"
        }
        
    # Match club
    club = None
    try:
        club = Clubs.objects.get(club_name__iexact=author_name)
    except Clubs.DoesNotExist:
        pass
        
    if not club:
        # Fuzzy match using string cleaning and similarity utilities
        from utils.scraping_utils import jaccard_similarity, sequence_similarity
        clubs = Clubs.objects.all()
        best_match = None
        best_score = 0.0
        for c in clubs:
            c_cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", c.club_name.lower())
            author_cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", author_name.lower())
            
            if c_cleaned in author_cleaned or author_cleaned in c_cleaned:
                score = len(c_cleaned) / len(author_cleaned) if len(author_cleaned) > len(c_cleaned) else len(author_cleaned) / len(c_cleaned)
                if score > best_score:
                    best_score = score
                    best_match = c
            else:
                score = max(jaccard_similarity(c.club_name, author_name), sequence_similarity(c.club_name, author_name))
                if score > 0.7 and score > best_score:
                    best_score = score
                    best_match = c
        if best_match and best_score >= 0.6:
            club = best_match
            logger.info(f"[Discord] [{message_id}] Fuzzy matched author '{author_name}' to club '{club.club_name}' (score: {best_score:.2f})")
            
    # Resolve ig_handle and club_type
    ig_handle = None
    club_type = None
    if club:
        club_type = club.club_type
        if club.ig:
            ig_handle = club.ig.rstrip("/").split("/")[-1]
            
    if not ig_handle:
        ig_handle = re.sub(r"[^a-z0-9_]", "", author_name.lower().replace(" ", "_"))
        
    # Parse timestamp
    posted_at = None
    timestamp_str = data.get("timestamp")
    if timestamp_str:
        try:
            posted_at = parse_utc_datetime(timestamp_str)
        except Exception:
            pass
    if not posted_at:
        posted_at = timezone.now()
        
    # Upload images to S3
    attachments = data.get("attachments", [])
    all_s3_urls = []
    for img_url in attachments:
        if img_url:
            try:
                s3_url = upload_image_from_url(img_url)
                if s3_url:
                    all_s3_urls.append(s3_url)
            except Exception as e:
                logger.error(f"[Discord] [{message_id}] Failed to upload image {img_url} to S3: {e}")
                
    # Run event extraction via OpenAI
    logger.info(f"[Discord] [{message_id}] Extracting event details from text: {content[:100]}...")
    try:
        extracted_events = extract_events_from_caption(
            caption_text=content,
            all_s3_urls=all_s3_urls,
            post_created_at=posted_at,
            school="University of Waterloo"
        )
    except Exception as e:
        logger.error(f"[Discord] [{message_id}] OpenAI extraction failed: {e}")
        return {
            "status": "error",
            "message": f"OpenAI extraction failed: {e}"
        }
        
    if not extracted_events:
        logger.info(f"[Discord] [{message_id}] No events found in Discord message.")
        return {
            "status": "no_events_found",
            "message": "No events could be extracted from the message content"
        }
        
    if not isinstance(extracted_events, list):
        extracted_events = [extracted_events]
        
    # Save events to database
    saved_count = 0
    saved_events_data = []
    for event_data in extracted_events:
        event_data["ig_handle"] = ig_handle
        event_data["discord_handle"] = author_name
        event_data["source_url"] = source_url
        event_data["school"] = "University of Waterloo"
        event_data["posted_at"] = posted_at
        event_data["likes_count"] = 0
        event_data["comments_count"] = 0
        event_data["club_type"] = club_type
        
        # Check for past date
        occurrences = event_data.get("occurrences", [])
        if occurrences:
            first_occurrence = occurrences[0]
            dtstart_utc = parse_utc_datetime(first_occurrence.get("dtstart_utc"))
            if dtstart_utc and dtstart_utc < timezone.now():
                logger.info(f"[Discord] [{message_id}] Skipping event '{event_data.get('title')}' - date {dtstart_utc} is in the past")
                continue
                
        # Set source image
        image_idx = event_data.get("image_index")
        if (
            image_idx is not None
            and isinstance(image_idx, int)
            and 0 <= image_idx < len(all_s3_urls)
        ):
            event_data["source_image_url"] = all_s3_urls[image_idx]
        else:
            event_data["source_image_url"] = all_s3_urls[0] if all_s3_urls else ""
            
        try:
            result = insert_event_to_db(event_data)
            if result is True or result == "updated":
                saved_count += 1
                saved_events_data.append({
                    "title": event_data.get("title"),
                    "location": event_data.get("location"),
                    "dtstart_utc": occurrences[0].get("dtstart_utc") if occurrences else None,
                    "status": "updated" if result == "updated" else "created"
                })
        except Exception as e:
            logger.error(f"[Discord] [{message_id}] Error saving event to DB: {e}")
            
    return {
        "status": "success",
        "processed_count": len(extracted_events),
        "saved_count": saved_count,
        "events": saved_events_data
    }
