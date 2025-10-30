import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

import csv
import json
import random
import re
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from dateutil import parser as dateutil_parser

import requests
from requests.exceptions import ReadTimeout, ConnectionError
from django.utils import timezone
from dotenv import load_dotenv
from instaloader import Instaloader

from apps.clubs.models import Clubs
from apps.events.models import Events
from scraping.logging_config import logger
from scraping.zyte_setup import setup_zyte
from services.openai_service import (
    extract_events_from_caption,
    generate_event_embedding,
)
from services.storage_service import upload_image_from_url
from shared.constants.user_agents import USER_AGENTS
from utils.embedding_utils import find_similar_events
from utils.events_utils import tz_compute

MAX_POSTS = int(os.getenv("MAX_POSTS", "100"))
MAX_CONSEC_OLD_POSTS = 10
CUTOFF_DAYS = int(os.getenv("CUTOFF_DAYS", "2"))

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
CSRFTOKEN = os.getenv("CSRFTOKEN")
SESSIONID = os.getenv("SESSIONID")
DS_USER_ID = os.getenv("DS_USER_ID")
MID = os.getenv("MID")
IG_DID = os.getenv("IG_DID")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")


def get_post_image_url(post):
    try:
        if post._node.get("image_versions2"):
            return post._node["image_versions2"]["candidates"][0]["url"]

        if post._node.get("carousel_media"):
            return post._node["carousel_media"][0]["image_versions2"]["candidates"][0][
                "url"
            ]

        if post._node.get("display_url"):
            return post._node["display_url"]
        return None
    except (KeyError, AttributeError) as e:
        logger.error(
            f"Error accessing image URL for post {getattr(post, 'shortcode', 'unknown')}: {e!s}"
        )
        return None


def extract_s3_filename_from_url(image_url: str) -> str:
    if not image_url:
        return None
    filename = image_url.split("/")[-1]
    return f"events/{filename}"


def normalize_string(s):
    if not s:
        return ""
    return re.sub(r"\W+", "", s).lower().strip()


def is_duplicate_event(event_data):
    """Check for duplicate events (same name, date, location, time)"""
    title = normalize_string(event_data.get("title"))
    location = normalize_string(event_data.get("location"))
    date = datetime.fromisoformat(event_data.get("dtstart")).date()

    try:
        candidates = Events.objects.filter(dtstart__date=date)
        for c in candidates:
            c_title = normalize_string(getattr(c, "title", ""))
            c_loc = normalize_string(getattr(c, "location", ""))
            if c_title == title and c_loc == location:
                return True
    except Exception as e:
        logger.error(f"Error during duplicate check: {e!s}")
    return False


def append_event_to_csv(
    event_data,
    ig_handle,
    source_url,
    added_to_db="success",
    embedding=None,
    club_type=None,
):
    csv_file = Path(__file__).resolve().parent / "events_scraped.csv"
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_file.exists()

    dtstart_raw = event_data.get("dtstart")
    dtend_raw = event_data.get("dtend")
    dtstart = dateutil_parser.parse(dtstart_raw).replace(tzinfo=None) if dtstart_raw else ""
    dtend = dateutil_parser.parse(dtend_raw).replace(tzinfo=None) if dtend_raw else ""

    dtstart_utc = event_data.get("dtstart_utc", "")
    dtend_utc = event_data.get("dtend_utc", "")
    duration = event_data.get("duration", "")
    all_day = event_data.get("all_day", False)
    location = event_data.get("location", "")
    food = event_data.get("food", "")
    price = event_data.get("price", "")
    registration = bool(event_data.get("registration", False))
    description = event_data.get("description", "")
    rrule = event_data.get("rrule", "")
    latitude = event_data.get("latitude", None)
    longitude = event_data.get("longitude", None)
    tz = event_data.get("tz", "")
    school = event_data.get("school", "")
    source_image_url = event_data.get("source_image_url", "")
    title = event_data.get("title", "")

    fieldnames = [
        "ig_handle",
        "title",
        "source_url",
        "dtstart",
        "dtstart_utc",
        "dtend",
        "dtend_utc",
        "duration",
        "location",
        "food",
        "price",
        "registration",
        "description",
        "rrule",
        "latitude",
        "longitude",
        "tz",
        "school",
        "source_image_url",
        "all_day",
        "club_type",
        "raw_json",
        "added_to_db",
        "status",
        "embedding",
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
                "dtstart": dtstart,
                "dtstart_utc": dtstart_utc,
                "dtend": dtend,
                "dtend_utc": dtend_utc,
                "duration": duration,
                "location": location,
                "food": food,
                "price": price,
                "registration": registration,
                "description": description,
                "rrule": rrule,
                "latitude": latitude,
                "longitude": longitude,
                "tz": tz,
                "school": school,
                "source_image_url": source_image_url,
                "all_day": all_day,
                "club_type": club_type or event_data.get("club_type") or "",
                "raw_json": json.dumps(event_data, ensure_ascii=False),
                "added_to_db": added_to_db,
                "status": "CONFIRMED",
                "embedding": embedding or "",
            }
        )
        logger.info(f"Event written to CSV with status: {added_to_db}")


def insert_event_to_db(event_data, ig_handle, source_url):
    """Map scraped event data to Event model fields, insert to DB"""
    title = event_data.get("title")
    dtstart = dateutil_parser.parse(event_data.get("dtstart")).replace(tzinfo=None)
    dtend = dateutil_parser.parse(event_data.get("dtend")).replace(tzinfo=None) \
        if event_data.get("dtend") else None
    source_image_url = event_data.get("source_image_url") or ""
    description = event_data.get("description") or ""
    location = event_data.get("location")
    price = event_data.get("price", None)
    food = event_data.get("food", None)
    registration = bool(event_data.get("registration", False))
    embedding = event_data.get("embedding") or ""
    date = dtstart.date()
    dtstart_utc, dtend_utc, duration, all_day = tz_compute(dtstart, dtend)
    tz = event_data.get("tz", "")
    latitude = event_data.get("latitude", None)
    longitude = event_data.get("longitude", None)
    school = event_data.get("school", "")

    if is_duplicate_event(event_data):
        logger.info(
            f"Duplicate event detected, skipping {title} on {date} at {location}"
        )
        return False

    # Get club_type by matching ig_handle from Events to ig of Clubs
    try:
        club = Clubs.objects.get(ig=ig_handle)
        club_type = club.club_type
    except Clubs.DoesNotExist:
        club_type = None
        logger.warning(
            f"Club with handle {ig_handle} not found, inserting event with club_type NULL"
        )

    if not embedding:
        try:
            embedding = generate_event_embedding(event_data)
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e!s}")

    # Similarlity check deduplication
    try:
        similar_events = find_similar_events(
            embedding, threshold=0.90, limit=10, min_date=date
        )
        candidate_ids = [row["id"] for row in similar_events]
        if candidate_ids:
            qs = Events.objects.filter(id__in=candidate_ids, dtstart__date=date)
            for existing in qs:
                # Only replace if new event has image but existing doesn't,
                # or if new description is longer (more info)
                new_img = source_image_url
                old_img = getattr(existing, "source_image_url", None)
                new_desc = description or ""
                old_desc = existing.description or ""
                if (not old_img and new_img) or (len(new_desc) > len(old_desc) + 10):
                    logger.info(f"Replacing older event #{existing.id} with newer one")
                    existing.delete()
    except Exception as e:
        logger.error(f"Unexpected error finding duplicates by similarity check: {e}")

    create_kwargs = {
        "ig_handle": ig_handle,
        "title": title,
        "source_url": source_url,
        "dtstamp": timezone.now(),
        "dtstart": dtstart,
        "dtstart_utc": dtstart_utc,
        "dtend": dtend or None,
        "dtend_utc": dtend_utc,
        "duration": duration,
        "club_type": club_type,
        "location": location,
        "food": food or None,
        "price": price or None,
        "registration": registration,
        "description": description or None,
        "reactions": {},
        "embedding": embedding or None,
        "source_image_url": source_image_url or None,
        "raw_json": event_data,
        "status": "CONFIRMED",
        "tz": tz,
        "all_day": all_day,
        "latitude": latitude,
        "longitude": longitude,
        "school": school,
        "rrule": event_data.get("rrule", ""),
    }

    try:
        Events.objects.create(**create_kwargs)
        append_event_to_csv(
            event_data,
            ig_handle,
            source_url,
            added_to_db="success",
            embedding=embedding,
            club_type=club_type,
        )
        logger.info("Event added successfully")
        return True
    except Exception as e:
        logger.error(f"Error inserting event to DB: {e}")
        try:
            append_event_to_csv(
                event_data,
                ig_handle,
                source_url,
                added_to_db="failed",
                embedding=embedding,
                club_type=club_type,
            )
        except Exception as csv_e:
            logger.error(f"Error writing event to CSV after DB failure: {csv_e}")
        return False


def get_seen_shortcodes():
    """Fetches all post shortcodes from events table in DB"""
    logger.info("Fetching seen shortcodes from the database...")
    try:
        events = Events.objects.filter(source_url__isnull=False).values_list(
            "source_url", flat=True
        )
        shortcodes = {url.split("/")[-2] for url in events if url}
        return shortcodes
    except Exception as e:
        logger.error(f"Could not fetch shortcodes from database: {e}")
        return set()


def safe_feed_posts(loader, retries=3, backoff=60):
    """
    Yield posts from loader.get_feed_posts(), retrying on network errors.
    On error, re-instantiate the session and skip already-yielded posts.
    """
    seen_shortcodes = set()
    attempts = 0
    while attempts < retries:
        try:
            for post in loader.get_feed_posts():
                if hasattr(post, "shortcode"):
                    if post.shortcode in seen_shortcodes:
                        continue
                    seen_shortcodes.add(post.shortcode)
                yield post
            break  # Finished all posts
        except (ReadTimeout, ConnectionError) as e:
            attempts += 1
            logger.warning(f"Network error: {e!s}. Retrying in {backoff} seconds (attempt {attempts}/{retries})...")
            time.sleep(backoff)
            try:
                new_loader = session()
                loader.__dict__.update(new_loader.__dict__)
                logger.info("Session re-instantiated successfully. Continuing feed scrape.")
            except Exception as session_e:
                logger.error(f"Failed to re-instantiate session: {session_e}")
                break
    if attempts >= retries:
        logger.error("Too many consecutive network errors. Aborting feed scrape.")


def process_recent_feed(
    loader,
    cutoff=None,
    max_posts=MAX_POSTS,
    max_consec_old_posts=MAX_CONSEC_OLD_POSTS,
):
    """
    Process Instagram feed posts and extract event info.
    Stops scraping once posts become older than cutoff.
    """
    if not cutoff:
        cutoff = timezone.now() - timedelta(days=CUTOFF_DAYS)

    events_added = 0
    posts_processed = 0
    consec_old_posts = 0
    termination_reason = None
    logger.info(f"Starting feed processing with cutoff: {cutoff}")

    seen_shortcodes = get_seen_shortcodes()

    def check_post_limit():
        nonlocal termination_reason
        if posts_processed >= max_posts:
            termination_reason = f"reached_max_posts={max_posts}"
            logger.info(f"Reached max post limit of {max_posts}, stopping")
            return True
        return False

    try:
        for post in safe_feed_posts(loader):
            try:
                post_time = timezone.make_aware(post.date_utc) if timezone.is_naive(post.date_utc) else post.date_utc
                if post.shortcode in seen_shortcodes or post_time < cutoff:
                    consec_old_posts += 1
                    logger.debug(
                        f"[{post.shortcode}] [{post.owner_username}] Skipping post; consec_old_posts={consec_old_posts}"
                    )
                    if consec_old_posts >= max_consec_old_posts:
                        termination_reason = (
                            f"reached_consecutive_old_posts={max_consec_old_posts}"
                        )
                        logger.info(
                            f"Reached {max_consec_old_posts} consecutive old posts, stopping."
                        )
                        break
                    continue

                consec_old_posts = 0
                logger.info("-" * 100)
                logger.info(f"[{post.shortcode}] [{post.owner_username}] Processing post")

                # Safely get image URL and upload to S3
                raw_image_url = get_post_image_url(post)
                if raw_image_url:
                    time.sleep(random.uniform(1, 3))
                    source_image_url = upload_image_from_url(raw_image_url)
                    logger.debug(f"[{post.shortcode}] [{post.owner_username}] Uploaded image to S3: {source_image_url}")
                else:
                    logger.warning(
                        f"[{post.shortcode}] [{post.owner_username}] No image URL found for post, skipping image upload"
                    )
                    source_image_url = None

                posts_processed += 1
                event_data = extract_events_from_caption(
                    post.caption, source_image_url, post.date_utc
                )
                if not event_data:
                    logger.warning(
                        f"[{post.shortcode}] [{post.owner_username}] AI client returned no event for post"
                    )
                    if check_post_limit():
                        break
                    continue

                logger.debug(f"[{post.shortcode}] [{post.owner_username}] Event data: {json.dumps(event_data, ensure_ascii=False, separators=(',', ':'))}")
                source_url = f"https://www.instagram.com/p/{post.shortcode}/"
                today = timezone.now().date()

                if not (
                    event_data.get("title")
                    and event_data.get("dtstart")
                    and event_data.get("location")
                ):
                    missing_fields = [
                        key
                        for key in ["title", "dtstart", "location"]
                        if not event_data.get(key)
                    ]
                    logger.warning(
                        f"[{post.shortcode}] [{post.owner_username}] Missing required fields for event '{event_data.get('title', 'Unknown')}': {missing_fields}, skipping event"
                    )
                    embedding = generate_event_embedding(event_data)
                    append_event_to_csv(
                        event_data,
                        post.owner_username,
                        source_url,
                        added_to_db="missing_fields",
                        embedding=embedding,
                    )
                    if check_post_limit():
                        break
                    continue

                date = datetime.fromisoformat(event_data.get("dtstart")).date()
                if date < today:
                    logger.info(
                        f"[{post.shortcode}] [{post.owner_username}] Skipping event '{event_data.get('title')}' with past date {date}"
                    )
                    if check_post_limit():
                        break
                    continue

                if insert_event_to_db(event_data, post.owner_username, source_url):
                    events_added += 1
                    logger.info(
                        f"[{post.shortcode}] [{post.owner_username}] Successfully added event '{event_data.get('title')}'"
                    )
                else:
                    logger.error(
                        f"[{post.shortcode}] [{post.owner_username}] Failed to add event '{event_data.get('title')}'"
                    )

                if check_post_limit():
                    break

                seen_shortcodes.add(post.shortcode)
                time.sleep(random.uniform(30, 60))

            except Exception as e:
                logger.error(
                    f"[{post.shortcode}] [{post.owner_username}] Error processing post: {e!s}"
                )
                logger.error(f"[{post.shortcode}] [{post.owner_username}] Traceback: {traceback.format_exc()}")
                time.sleep(random.uniform(3, 8))
                continue

        if not termination_reason:
            termination_reason = "no_more_posts"

    except Exception as e:
        # Top-level errors (e.g., loader failure / auth)
        termination_reason = "error"
        logger.error(f"Feed processing aborted due to error: {e!s}")
        logger.error(f"Traceback: {traceback.format_exc()}")

    logger.debug(
        "Feed processing completed. reason=%s, posts_processed=%d, events_added=%d",
        termination_reason,
        posts_processed,
        events_added,
    )
    logger.info("\n------------------------- Summary -------------------------")
    logger.info(f"Added {events_added} event(s) to Supabase")


def test_zyte_proxy(country="CA"):
    """
    Patch requests.Session to route through Zyte with geolocation,
    test Zyte proxy routing and geolocation
    """
    zyte_cert_path = setup_zyte()
    zyte_proxy = os.getenv("ZYTE_PROXY")
    logger.debug(f"Zyte proxy config: proxy={zyte_proxy!r}, cert={zyte_cert_path!s}")

    if not zyte_proxy:
        logger.warning(
            "ZYTE_PROXY not set - skipping proxied geolocation test and trying direct request"
        )
        try:
            resp = requests.get("https://ipapi.co/json/", timeout=15)
            resp.raise_for_status()
            logger.info("Direct geolocation test succeeded")
            return True
        except Exception as e:
            logger.warning(f"Direct geolocation test failed: {e!s}")
            return False

    old_request = requests.Session.request

    def zyte_request(self, method, url, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Zyte-Geolocation"] = country
        kwargs["headers"] = headers
        kwargs["proxies"] = {"http": zyte_proxy, "https": zyte_proxy}
        if zyte_cert_path:
            kwargs["verify"] = str(zyte_cert_path)
        kwargs["timeout"] = kwargs.get("timeout", 30)
        return old_request(self, method, url, **kwargs)

    requests.Session.request = zyte_request

    logger.debug(f"Testing Zyte proxy geolocation: {country}")
    try:
        resp = requests.get(
            "https://ipapi.co/json/",
            timeout=30,
            verify=str(zyte_cert_path) if zyte_cert_path else True,
            proxies={"http": zyte_proxy, "https": zyte_proxy},
        )
        resp.raise_for_status()
        data = resp.json()
        logger.debug("Connected via Zyte proxy")
        logger.debug(f"Public IP: {data.get('ip')}")
        logger.debug(f"Country: {data.get('country_name')} ({data.get('country')})")
        logger.debug(f"City: {data.get('city')}")
    except Exception as e:
        logger.warning(f"Proxied geolocation failed: {e!s}")
    return True


def session():
    L = Instaloader(user_agent=random.choice(USER_AGENTS))
    try:
        SESSION_CACHE_DIR = Path(os.getenv("GITHUB_WORKSPACE", ".")) / ".insta_cache"
        SESSION_CACHE_DIR.mkdir(exist_ok=True)
        files = [p for p in SESSION_CACHE_DIR.iterdir() if p.is_file()]
        session_file = files[0] if files else SESSION_CACHE_DIR / f"session-{USERNAME}"
    except Exception:
        session_file = Path(__file__).resolve().parent.parent / ("session-" + USERNAME)
    try:
        if session_file.exists():
            L.load_session_from_file(USERNAME, filename=str(session_file))
            logger.info(f"Loaded session from file: {session_file!s}")
        else:
            logger.info("No session file found, falling back to env")
            L.load_session(
                USERNAME,
                {
                    "csrftoken": CSRFTOKEN,
                    "sessionid": SESSIONID,
                    "ds_user_id": DS_USER_ID,
                    "mid": MID,
                    "ig_did": IG_DID,
                },
            )
        L.save_session_to_file(filename=str(session_file))
        return L
    except Exception as e:
        logger.error(f"Failed to load session: {e}")
        raise


if __name__ == "__main__":
    test_zyte_proxy("CA")
    logger.info("Attemping to load Instagram session...")
    L = session()
    L.context.request_timeout = 120
    if L:
        logger.info("Session created successfully!")
        process_recent_feed(L)
    else:
        logger.critical("Failed to initialize Instagram session, stopping...")
