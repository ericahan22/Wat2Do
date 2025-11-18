import asyncio
import os
import sys
from functools import lru_cache

# Set up Django
if "django" not in sys.modules:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()

from asgiref.sync import sync_to_async

from apps.clubs.models import Clubs
from apps.events.models import Events, IgnoredPost
from scraping.logging_config import logger
from services.storage_service import upload_image_from_url
from utils.date_utils import parse_utc_datetime
from utils.scraping_utils import insert_event_to_db


class EventProcessor:
    def __init__(self, concurrency=5):
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)

    @staticmethod
    @lru_cache(maxsize=512)
    def _get_club_type(ig_handle):
        try:
            return Clubs.objects.get(ig=ig_handle).club_type
        except Clubs.DoesNotExist:
            return None

    @sync_to_async(thread_sensitive=True)
    def _get_seen_shortcodes(self):
        """Fetch existing shortcodes to avoid processing duplicates."""
        try:
            # Get shortcodes from successful events
            events = Events.objects.filter(source_url__contains="/p/").values_list("source_url", flat=True)
            event_codes = {url.strip("/").split("/")[-1] for url in events}
            
            # Get shortcodes from explicitly ignored posts
            ignored = IgnoredPost.objects.values_list("shortcode", flat=True)
            
            return event_codes.union(ignored)
        except Exception as e:
            logger.error(f"Error fetching seen shortcodes: {e}")
            return set()

    # --- Async Wrappers ---
    @sync_to_async(thread_sensitive=False)
    def _upload_image(self, url):
        return upload_image_from_url(url)

    @sync_to_async(thread_sensitive=False)
    def _extract_events(self, caption, img_url, post_time):
        from services.openai_service import extract_events_from_caption
        return extract_events_from_caption(caption, img_url, post_time)

    @sync_to_async(thread_sensitive=True)
    def _save_event(self, event_data, ig_handle, source_url, club_type):
        return insert_event_to_db(event_data, ig_handle, source_url, club_type)

    @sync_to_async(thread_sensitive=True)
    def _ignore_post(self, shortcode):
        IgnoredPost.objects.get_or_create(shortcode=shortcode)

    async def _process_single_post_extraction(self, post):
        """Extracts event data from a single post using OpenAI."""
        async with self.semaphore:
            timestamp_str = post.get("timestamp")
            post_dt = parse_utc_datetime(timestamp_str)

            return await self._extract_events(
                post.get("caption"),
                post.get("source_image_url"), # Using S3 URL
                post_dt
            )

    async def process(self, posts_data, cutoff_date):
        """Main entry point to process a list of raw posts."""
        logger.info(f"Processing {len(posts_data)} posts...")
        
        seen_shortcodes = await self._get_seen_shortcodes()
        valid_posts = []

        # 1. Filter Posts
        for post in posts_data:
            url = post.get("url")
            if not url or "/p/" not in url: continue
            
            # Basic validation
            if not post.get("caption") or not post.get("displayUrl"): continue

            # Date Check
            post_dt = parse_utc_datetime(post.get("timestamp"))
            if not post_dt or post_dt < cutoff_date: continue

            # Duplicate Check
            shortcode = url.strip("/").split("/")[-1]
            if shortcode in seen_shortcodes: continue

            valid_posts.append(post)

        if not valid_posts:
            logger.info("No new valid posts found.")
            return

        logger.info(f"Found {len(valid_posts)} new posts. Starting image uploads...")

        # 2. Upload Images
        upload_tasks = [self._upload_image(p.get("displayUrl")) for p in valid_posts]
        s3_urls = await asyncio.gather(*upload_tasks)
        for post, s3_url in zip(valid_posts, s3_urls, strict=False):
            post["source_image_url"] = s3_url

        # 3. Extract Events
        logger.info("Extracting event data...")
        extract_tasks = [self._process_single_post_extraction(p) for p in valid_posts]
        results = await asyncio.gather(*extract_tasks)

        # 4. Save to DB
        saved_count = 0
        for post, extracted_events in zip(valid_posts, results, strict=False):
            ig_handle = post.get("ownerUsername")
            source_url = post.get("url")
            shortcode = source_url.strip("/").split("/")[-1]
            club_type = self._get_club_type(ig_handle)

            if not extracted_events:
                # Mark as ignored if AI found nothing
                await self._ignore_post(shortcode)
                continue

            for event_data in extracted_events:
                success = await self._save_event(event_data, ig_handle, source_url, club_type)
                if success: saved_count += 1

        logger.info(f"Processing complete. Saved {saved_count} new events.")
