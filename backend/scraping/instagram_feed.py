import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

import asyncio
from asgiref.sync import sync_to_async
import csv
import json
import traceback
from datetime import timedelta
from pathlib import Path

from apify_client import ApifyClient
from django.utils import timezone
from dotenv import load_dotenv

from apps.clubs.models import Clubs
from apps.events.models import EventDates, Events, IgnoredPost
from scraping.logging_config import logger
from shared.constants.urls_to_scrape import FULL_URLS
from services.storage_service import upload_image_from_url
from utils.date_utils import parse_utc_datetime
from utils.scraping_utils import (
    jaccard_similarity,
    normalize,
    sequence_similarity,
)


# Load environment variables from .env file
load_dotenv()

CUTOFF_DAYS = 1
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")


def is_duplicate_event(event_data):
    """Check for duplicate events using title, occurrences, location, and description."""

    title = event_data.get("title") or ""
    location = event_data.get("location") or ""
    description = event_data.get("description") or ""
    occurrences = event_data.get("occurrences")

    if not occurrences:
        return False

    target_start_str = occurrences[0].get("dtstart_utc")
    target_start = parse_utc_datetime(target_start_str)
    if not target_start:
        return False

    try:
        candidates = EventDates.objects.select_related("event").filter(
            dtstart_utc__date=target_start.date()
        )

        for candidate in candidates:
            existing_event = candidate.event
            if not existing_event:
                continue

            c_title = getattr(existing_event, "title", "") or ""
            c_loc = getattr(existing_event, "location", "") or ""
            c_desc = getattr(existing_event, "description", "") or ""
            c_start = candidate.dtstart_utc

            if not c_start:
                continue

            # Compare same-day occurrences with fuzzy matching on title/location/description.
            if c_start.date() != target_start.date():
                continue

            norm_title = normalize(title)
            norm_c_title = normalize(c_title)
            substring_match = norm_c_title in norm_title or norm_title in norm_c_title

            title_sim = max(
                jaccard_similarity(c_title, title),
                sequence_similarity(c_title, title),
            )
            loc_sim = jaccard_similarity(c_loc, location)
            desc_sim = jaccard_similarity(c_desc, description)

            if substring_match:
                logger.warning(
                    f"Duplicate by substring match: '{title}' @ '{location}' matches '{c_title}' @ '{c_loc}'"
                )
                return True

            if (title_sim > 0.7 and loc_sim > 0.5) or (
                loc_sim > 0.5 and desc_sim > 0.3
            ):
                logger.warning(
                    f"Duplicate by similarity: '{title}' @ '{location}' matches '{c_title}' @ '{c_loc}' "
                    f"(title_sim={title_sim:.3f}, loc_sim={loc_sim:.3f}, desc_sim={desc_sim:.3f})"
                )
                return True
    except Exception as exc:
        logger.error(f"Error during duplicate check: {exc!s}")

    return False


def append_event_to_csv(
    event_data,
    ig_handle,
    source_url,
    added_to_db="success",
    club_type=None,
):
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    csv_file = logs_dir / "events_scraped.csv"

    file_exists = csv_file.exists()

    occurrences = event_data.get("occurrences", []) or []
    primary_occurrence = occurrences[0] if occurrences else {}

    dtstart_utc = primary_occurrence.get("dtstart_utc")
    dtend_utc = primary_occurrence.get("dtend_utc")
    duration = primary_occurrence.get("duration")
    tz = primary_occurrence.get("tz")
    location = event_data.get("location", "")
    food = event_data.get("food", "")
    price = event_data.get("price", "")
    registration = bool(event_data.get("registration", False))
    description = event_data.get("description", "")
    latitude = event_data.get("latitude", None)
    longitude = event_data.get("longitude", None)
    school = event_data.get("school", "")
    source_image_url = event_data.get("source_image_url", "")
    title = event_data.get("title", "")
    categories = event_data.get("categories", [])

    fieldnames = [
        "ig_handle",
        "title",
        "source_url",
        "dtstart_utc",
        "dtend_utc",
        "duration",
        "location",
        "food",
        "price",
        "registration",
        "description",
        "latitude",
        "longitude",
        "tz",
        "school",
        "source_image_url",
        "club_type",
        "categories",
        "occurrences",
        "added_to_db",
        "status",
    ]

    with open(csv_file, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "ig_handle": ig_handle,
                "title": title,
                "source_url": source_url,
                "dtstart_utc": dtstart_utc,
                "dtend_utc": dtend_utc,
                "duration": duration,
                "location": location,
                "food": food,
                "price": price,
                "registration": registration,
                "description": description,
                "latitude": latitude,
                "longitude": longitude,
                "tz": tz,
                "school": school,
                "source_image_url": source_image_url,
                "club_type": club_type or event_data.get("club_type") or "",
                "categories": json.dumps(categories, ensure_ascii=False),
                "occurrences": json.dumps(occurrences, ensure_ascii=False),
                "added_to_db": added_to_db,
                "status": "CONFIRMED",
            }
        )
        logger.info(f"Event written to CSV with status: {added_to_db}")


def insert_event_to_db(event_data, ig_handle, source_url):
    """Map scraped event data to Event model fields, insert to DB"""
    title = event_data.get("title", "")
    source_image_url = event_data.get("source_image_url") or ""
    description = event_data.get("description", "") or ""
    location = event_data.get("location")
    price = event_data.get("price", None)
    food = event_data.get("food", None)
    registration = bool(event_data.get("registration", False))
    school = event_data.get("school", "")
    categories = event_data.get("categories", [])
    occurrences = event_data.get("occurrences")

    if not occurrences:
        logger.warning(f"Event '{title}' missing occurrences; skipping insert")
        return "missing_occurrence"

    if not categories or not isinstance(categories, list):
        logger.warning(f"Event '{title}' missing categories, assigning 'Uncategorized'")
        categories = ["Uncategorized"]

    if is_duplicate_event(event_data):
        return "duplicate"

    # Get club_type by matching ig_handle from Events to ig of Clubs
    try:
        club = Clubs.objects.get(ig=ig_handle)
        club_type = club.club_type
    except Clubs.DoesNotExist:
        club_type = None
        logger.warning(
            f"Club with handle {ig_handle} not found, inserting event with club_type NULL"
        )

    create_kwargs = {
        "ig_handle": ig_handle,
        "title": title,
        "source_url": source_url,
        "club_type": club_type,
        "location": location,
        "food": food or None,
        "price": price or None,
        "registration": registration,
        "description": description or None,
        "reactions": {},
        "source_image_url": source_image_url or None,
        "status": "CONFIRMED",
        "school": school,
        "categories": categories,
    }

    try:
        event = Events.objects.create(**create_kwargs)
        event_dates = []

        for occ in occurrences:
            dtstart_utc = parse_utc_datetime(occ.get("dtstart_utc"))
            dtend_utc_raw = occ.get("dtend_utc")
            dtend_utc = (
                parse_utc_datetime(dtend_utc_raw)
                if dtend_utc_raw and dtend_utc_raw.strip()
                else None
            )

            event_dates.append(
                EventDates(
                    event=event,
                    dtstart_utc=dtstart_utc,
                    dtend_utc=dtend_utc,
                    duration=occ.get("duration") or None,
                    tz=occ.get("tz") or None,
                )
            )

        EventDates.objects.bulk_create(event_dates)
        logger.debug(
            f"Created {len(event_dates)} EventDates entries for event {event.id}"
        )
        return True
    except Exception as e:
        logger.error(f"Error inserting event to DB: {e}")
        return False


def get_seen_shortcodes():
    """Fetches all post shortcodes from events and ignored posts tables in DB"""
    logger.info("Fetching seen shortcodes from the database...")
    try:
        events = Events.objects.filter(source_url__isnull=False).values_list(
            "source_url", flat=True
        )
        event_shortcodes = {
            url.strip("/").split("/")[-1]
            for url in events
            if url and "/p/" in url
        }
        ignored_shortcodes = set(
            IgnoredPost.objects.values_list("shortcode", flat=True)
        )
        shortcodes = event_shortcodes | ignored_shortcodes
        logger.info(f"Found {len(shortcodes)} seen shortcodes.")
        return shortcodes
    except Exception as e:
        logger.error(f"Could not fetch shortcodes from database: {e}")
        return set()


def get_apify_input(username=None):
    cutoff_date = timezone.now() - timedelta(days=CUTOFF_DAYS)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")
    logger.info(f"Setting post cutoff date to {cutoff_str} ({CUTOFF_DAYS} day ago)")

    if username:
        usernames = [username]
        logger.info(f"Scraping @{username}")
    else:
        usernames = []
        for url in FULL_URLS:
            try:
                clean_url = url.split("instagram.com/")[1]
                uname = clean_url.split("/")[0]
                if uname and uname not in usernames:
                    usernames.append(uname)
            except Exception:
                logger.warning(f"Could not parse username from URL: {url}")

    logger.info(f"Parsed {len(usernames)} unique usernames from the list.")

    actor_input = {
        "onlyPostsNewerThan": cutoff_str,
        "skipPinnedPosts": True,
        "username": usernames
    }
    return actor_input


async def process_single_post_async(post, semaphore, cutoff_date):
    """Asynchronously processes a single post."""
    
    # --- Wrappers for sync functions ---
    @sync_to_async(thread_sensitive=False)
    def async_upload_image(url):
        return upload_image_from_url(url)

    @sync_to_async(thread_sensitive=False)
    def async_extract_events(caption, img_url, post_time):
        from services.openai_service import extract_events_from_caption
        return extract_events_from_caption(caption, img_url, post_time)

    @sync_to_async(thread_sensitive=True)
    def async_insert_event_to_db(event_data, ig_handle, source_url):
        return insert_event_to_db(event_data, ig_handle, source_url)

    @sync_to_async(thread_sensitive=False)
    def async_append_event_to_csv(event_data, ig_handle, source_url, status):
        return append_event_to_csv(event_data, ig_handle, source_url, added_to_db=status)

    @sync_to_async(thread_sensitive=True)
    def async_ignore_post(shortcode):
        IgnoredPost.objects.get_or_create(shortcode=shortcode)

    shortcode = None
    events_added = 0
    
    async with semaphore:
        try:
            timestamp_str = post.get("timestamp")
            post_time_utc = parse_utc_datetime(timestamp_str)
            if not post_time_utc:
                logger.warning(f"Skipping post with unparseable timestamp: {timestamp_str}")
                return 0
            
            if post_time_utc < cutoff_date:
                logger.debug(f"Skipping post from {post_time_utc.date()} (older than cutoff {cutoff_date.date()})")
                return 0 

            # Map Apify fields
            owner_username = post.get("ownerUsername")
            caption = post.get("caption")
            source_url = post.get("url")
            raw_image_url = post.get("displayUrl")

            if not source_url or "/p/" not in source_url:
                logger.warning(f"Skipping item with invalid URL: {source_url}")
                return 0
            
            shortcode = source_url.strip("/").split("/")[-1]

            if not owner_username or not caption:
                logger.warning(
                    f"[{shortcode}] [{owner_username}] Skipping post with missing owner or caption."
                )
                return 0

            logger.info("--------------------------------------------------------------------------------")
            logger.info(f"[{shortcode}] [{owner_username}] Processing post...")

            # 1. Upload Image
            if raw_image_url:
                source_image_url = await async_upload_image(raw_image_url)
                logger.debug(f"[{shortcode}] [{owner_username}] Uploaded image to S3: {source_image_url}")
            else:
                source_image_url = None

            # 2. Extract Events
            extracted_list = await async_extract_events(caption, source_image_url, post_time_utc)

            if not extracted_list:
                logger.warning(f"[{shortcode}] [{owner_username}] AI client returned no events for post")
                return 0

            # 3. Process Events
            for idx, event_data in enumerate(extracted_list):
                added_to_db = None
                try:
                    logger.debug(
                        f"[{shortcode}] [{owner_username}] Event {idx + 1}/{len(extracted_list)}: {json.dumps(event_data, ensure_ascii=False, separators=(',', ':'))}"
                    )

                    if not (
                        event_data.get("title")
                        and event_data.get("location")
                        and event_data.get("occurrences")
                    ):
                        added_to_db = "missing_fields"
                        logger.warning(f"[{shortcode}] Missing required fields, skipping")
                        continue

                    first_occurrence = event_data.get("occurrences")[0]
                    dtstart_utc_str = first_occurrence.get("dtstart_utc")
                    dtstart_utc = parse_utc_datetime(dtstart_utc_str)
                    
                    if dtstart_utc and dtstart_utc < timezone.now():
                        added_to_db = "past_date"
                        logger.info(f"[{shortcode}] Skipping event with past date")
                        continue

                    # 4. Insert to DB
                    result = await async_insert_event_to_db(
                        event_data, owner_username, source_url
                    )
                    
                    if result is True:
                        events_added += 1
                        added_to_db = "success"
                        logger.info(f"[{shortcode}] Successfully added event '{event_data.get('title')}'")
                    elif result == "duplicate":
                        added_to_db = "duplicate"
                        logger.warning(f"[{shortcode}] Duplicate event, not added")
                    else:
                        added_to_db = "failed"
                        logger.error(f"[{shortcode}] Failed to add event")
                
                except Exception as inner_e:
                    logger.error(f"[{shortcode}] Error handling extracted event: {inner_e!s}")
                    added_to_db = "error"
                finally:
                    # 5. Append to CSV
                    await async_append_event_to_csv(
                        event_data,
                        owner_username,
                        source_url,
                        status=added_to_db or "unknown",
                    )
        
        except Exception as e:
            logger.error(f"[{shortcode or 'UNKNOWN'}] Error in async task: {e!s}")
            logger.error(f"[{shortcode or 'UNKNOWN'}] Traceback: {traceback.format_exc()}")
            return 0
        
        finally:
            # 6. Add to Ignored
            if shortcode:
                await async_ignore_post(shortcode)

        return events_added
        
    
async def process_scraped_posts(posts_data, cutoff_date):
    """
    Process Apify scraped posts concurrently using asyncio.
    """
    logger.info(f"Starting post processing for {len(posts_data)} scraped posts.")
    logger.info(f"Concurrency limit set to {MAX_CONCURRENT_TASKS} tasks.")

    seen_shortcodes = await sync_to_async(get_seen_shortcodes)()
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    tasks = []
    total_skipped_old = 0
    total_skipped_missing_data = 0
    
    # --- Pre-filter in main thread ---   
    valid_posts_to_process = []
    for post in posts_data:
        # 1. Check for valid URL
        source_url = post.get("url")
        if not source_url or "/p/" not in source_url:
            continue

        # 2. Check for required fields
        caption = post.get("caption")
        display_url = post.get("displayUrl")
        if not caption or not display_url:
            total_skipped_missing_data += 1
            continue
            
        # 3. Check date filter
        timestamp_str = post.get("timestamp")
        post_time_utc = parse_utc_datetime(timestamp_str)
        if not post_time_utc or post_time_utc < cutoff_date:
            total_skipped_old += 1
            continue
            
        # 4. Check if already seen in DB
        shortcode = source_url.strip("/").split("/")[-1]
        if shortcode in seen_shortcodes:
            logger.debug(f"[{shortcode}] Skipping previously seen post")
            continue
            
        valid_posts_to_process.append(post)

    logger.info(f"Skipped {total_skipped_old} old posts based on timestamp.")
    logger.info(f"Skipped {total_skipped_missing_data} posts missing caption or image.")
    logger.info(f"Found {len(valid_posts_to_process)} new posts not in DB.")

    for post in valid_posts_to_process:
        tasks.append(process_single_post_async(post, semaphore, cutoff_date))

    logger.info(f"Created {len(tasks)} new post tasks to run concurrently.")

    if not tasks:
        logger.info("No new posts to process.")
        logger.info("\n------------------------- Summary -------------------------")
        logger.info("Added 0 event(s) to Supabase")
        return

    # Process results
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_events_added = 0
    total_failures = 0
    for res in results:
        if isinstance(res, Exception):
            total_failures += 1
        else:
            total_events_added += int(res)

    logger.info(f"Feed processing completed.")
    logger.warning(f"{total_failures} tasks failed with errors.")
    logger.info("\n------------------------- Summary -------------------------")
    logger.info(f"Added {total_events_added} event(s) to Supabase")
    
    
def run_apify_scraper(username=None):
    """
    Initializes Apify client, runs the Instagram scraper,
    saves the raw results, and processes them.
    If username is provided, only scrape that user.
    """
    if not APIFY_API_TOKEN:
        logger.critical("APIFY_API_TOKEN not found in environment. Aborting.")
        return None

    posts_data = []
    try:
        client = ApifyClient(APIFY_API_TOKEN)
        actor_input = get_apify_input(username)
        logger.info("Starting Apify actor 'apify/instagram-post-scraper'...")
        run = client.actor("apify/instagram-post-scraper").call(run_input=actor_input)
        logger.info(f"Apify run started (ID: {run['id']}). Waiting for results...")
        
        for item in client.dataset(run['defaultDatasetId']).list_items().items:
            posts_data.append(item)

        logger.info(f"Successfully fetched {len(posts_data)} posts from Apify.")

        output_filename = "apify_raw_results.json"
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(posts_data, f, indent=4, ensure_ascii=False)
            logger.info(f"Saved {len(posts_data)} raw Apify results to {output_filename}")
        except Exception as e:
            logger.error(f"Failed to save raw results to JSON file: {e}")
        
        return posts_data

    except Exception as e:
        logger.error(f"An error occurred during the Apify scrape: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


if __name__ == "__main__":
    lock_file_path = Path(__file__).parent / "scrape.lock"
    if lock_file_path.exists():
        print("Scrape already in progress. Exiting.") 
        sys.exit()
    
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = logs_dir / "scraping.log"
    if log_file_path.exists():
        with open(log_file_path, 'w') as f:
            f.truncate(0)

    try:
        lock_file_path.touch()
        logger.info("--- Starting new scrape session ---")
        
        posts_data = run_apify_scraper()
        if posts_data is None:
            logger.warning("No data was loaded or fetched. Halting.")
        else:
            logger.info("Starting post processing...")
            cutoff_date = timezone.now() - timedelta(days=CUTOFF_DAYS)
            asyncio.run(process_scraped_posts(posts_data, cutoff_date))

    except Exception as e:
        logger.error(f"An uncaught exception occurred: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        if lock_file_path.exists():
            lock_file_path.unlink()
            logger.info("Removed scrape.lock")
        logger.info("--- Scraping session finished ---")
