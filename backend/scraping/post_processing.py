import os
import sys
import asyncio
from functools import lru_cache

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
from utils.scraping_utils import insert_event_to_db, append_event_to_csv

MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))

# --- Wrappers ---
@sync_to_async(thread_sensitive=True)
def async_insert_event_to_db(event_data, ig_handle, source_url, club_type=None):
    return insert_event_to_db(event_data, ig_handle, source_url, club_type)

@sync_to_async(thread_sensitive=False)
def async_append_event_to_csv(event_data, ig_handle, source_url, status):
    return append_event_to_csv(event_data, ig_handle, source_url, added_to_db=status)

@sync_to_async(thread_sensitive=True)
def async_ignore_post(shortcode):
    IgnoredPost.objects.get_or_create(shortcode=shortcode)

@sync_to_async(thread_sensitive=False)
def async_upload_image(url):
    return upload_image_from_url(url)

@sync_to_async(thread_sensitive=False)
def async_extract_events(caption, img_url, post_time):
    from services.openai_service import extract_events_from_caption
    return extract_events_from_caption(caption, img_url, post_time)

@lru_cache(maxsize=512)
def get_club_type_cached(ig_handle):
    try:
        club = Clubs.objects.get(ig=ig_handle)
        return club.club_type
    except Clubs.DoesNotExist:
        return None

def get_seen_shortcodes():
    logger.info("Fetching seen shortcodes from the database...")
    try:
        events = Events.objects.filter(source_url__isnull=False).values_list("source_url", flat=True)
        event_shortcodes = {url.strip("/").split("/")[-1] for url in events if url and "/p/" in url}
        ignored_shortcodes = set(IgnoredPost.objects.values_list("shortcode", flat=True))
        shortcodes = event_shortcodes | ignored_shortcodes
        logger.info(f"Found {len(shortcodes)} seen shortcodes.")
        return shortcodes
    except Exception as e:
        logger.error(f"Could not fetch shortcodes: {e}")
        return set()

async def batch_extract_events(posts, openai_semaphore):
    async def extract_one(post):
        async with openai_semaphore:
            # Parse string to datetime object
            timestamp_str = post.get("timestamp")
            post_dt = parse_utc_datetime(timestamp_str)
            
            return await async_extract_events(
                post.get("caption"),
                post.get("source_image_url"), # Use uploaded S3 URL
                post_dt
            )
    return await asyncio.gather(*[extract_one(post) for post in posts])

async def batch_upload_images(posts):
    async def upload_one(post):
        url = post.get("displayUrl")
        if url:
            return await async_upload_image(url)
        return None
    return await asyncio.gather(*[upload_one(post) for post in posts])

async def process_scraped_posts(posts_data, cutoff_date):
    logger.info(f"Starting post processing for {len(posts_data)} items.")
    
    seen_shortcodes = await sync_to_async(get_seen_shortcodes)()
    valid_posts = []
    
    for post in posts_data:
        source_url = post.get("url")
        if not source_url or "/p/" not in source_url:
            continue
            
        caption = post.get("caption")
        display_url = post.get("displayUrl")
        if not caption or not display_url:
            continue

        timestamp_str = post.get("timestamp")
        post_time_utc = parse_utc_datetime(timestamp_str)
        if not post_time_utc or post_time_utc < cutoff_date:
            continue

        shortcode = source_url.strip("/").split("/")[-1]
        if shortcode in seen_shortcodes:
            continue

        valid_posts.append(post)

    logger.info(f"Found {len(valid_posts)} new posts to process.")
    if not valid_posts:
        return

    # 1. Upload images
    logger.info("Uploading images...")
    image_urls = await batch_upload_images(valid_posts)
    for post, img_url in zip(valid_posts, image_urls):
        post["source_image_url"] = img_url

    # 2. Extract events
    logger.info("Extracting events...")
    openai_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    extracted_events_list = await batch_extract_events(valid_posts, openai_semaphore)

    # 3. Insert to DB
    for post, extracted_events in zip(valid_posts, extracted_events_list):
        ig_handle = post.get("ownerUsername")
        source_url = post.get("url")
        club_type = get_club_type_cached(ig_handle)
        
        if not extracted_events:
            # Ignore post if AI found nothing
            shortcode = source_url.strip("/").split("/")[-1]
            await async_ignore_post(shortcode)
            continue
            
        for event_data in extracted_events:
            await async_insert_event_to_db(event_data, ig_handle, source_url, club_type)

    logger.info("Processing completed.")
