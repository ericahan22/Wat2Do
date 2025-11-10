import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

import csv
import json
import random
import time
import traceback
from datetime import timedelta
from pathlib import Path

import requests
from requests.exceptions import ReadTimeout, ConnectionError
from django.utils import timezone
from dotenv import load_dotenv
from instaloader import Instaloader
from dateutil import parser

from apps.clubs.models import Clubs
from apps.events.models import Events, IgnoredPost, EventDates
from scraping.logging_config import logger
from scraping.zyte_setup import setup_zyte
from services.openai_service import (
    extract_events_from_caption,
)
from services.storage_service import upload_image_from_url
from shared.constants.user_agents import USER_AGENTS
from utils.scraping_utils import (
    normalize,
    jaccard_similarity,
    sequence_similarity,
    get_post_image_url,
)


MAX_POSTS = int(os.getenv("MAX_POSTS", "25"))
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


def is_duplicate_event(event_data):
    """Check for duplicate events using title, occurrences, location, and description."""

    title = event_data.get("title") or ""
    location = event_data.get("location") or ""
    description = event_data.get("description") or ""
    occurrences = event_data.get("occurrences")
    
    if not occurrences:
        return False

    target_start = occurrences[0].get("start_utc")
    if not target_start:
        return False

    try:
        candidates = (
            EventDates.objects.select_related("event")
            .filter(dtstart_utc__date=target_start.date())
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

            if (title_sim > 0.7 and loc_sim > 0.5) or (loc_sim > 0.5 and desc_sim > 0.3):
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

    dtstart_utc = primary_occurrence.get("start_utc")
    dtend_utc = primary_occurrence.get("end_utc")
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
    latitude = event_data.get("latitude", None)
    longitude = event_data.get("longitude", None)
    school = event_data.get("school", "")
    categories = event_data.get("categories", [])
    occurrences = event_data.get("occurrences")
    occurrences = event_data.get("occurrences")

    if not occurrences:
    if not occurrences:
        logger.warning(f"Event '{title}' missing occurrences; skipping insert")
        return "missing_occurrence"

    if not categories or not isinstance(categories, list):
        logger.warning(f"Event '{title}' missing categories, assigning 'Uncategorized'")
        categories = ["Uncategorized"]

    if is_duplicate_event(event_data):
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
        "dtstamp": timezone.now(),
        "club_type": club_type,
        "location": location,
        "food": food or None,
        "price": price or None,
        "registration": registration,
        "description": description or None,
        "reactions": {},
        "source_image_url": source_image_url or None,
        "status": "CONFIRMED",
        "latitude": latitude,
        "longitude": longitude,
        "school": school,
        "categories": categories,
    }

    try:
        event = Events.objects.create(**create_kwargs)
        event_dates = [
            EventDates(
                event=event,
                dtstart_utc=occ["start_utc"],
                dtend_utc=occ.get("end_utc"),
                duration=occ.get("duration"),
                tz=occ.get("tz"),
            )
            for occ in occurrences
        ]

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
        event_shortcodes = {url.split("/")[-2] for url in events if url}
        ignored_shortcodes = set(IgnoredPost.objects.values_list("shortcode", flat=True))
        shortcodes = event_shortcodes | ignored_shortcodes
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
                time.sleep(random.uniform(2, 4))
            break  # Finished all posts
        except (ReadTimeout, ConnectionError, requests.exceptions.SSLError) as e:
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
                if post_time < cutoff:
                    consec_old_posts += 1
                    logger.debug(
                        f"[{post.shortcode}] [{post.owner_username}] Skipping old post; consec_old_posts={consec_old_posts}"
                    )
                    continue
                if post.shortcode in seen_shortcodes:
                    logger.debug(
                        f"[{post.shortcode}] [{post.owner_username}] Skipping previously seen post"
                    )
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

                extracted_list = extract_events_from_caption(
                    post.caption, source_image_url, post.date_local
                )
                if not extracted_list:
                    logger.warning(
                        f"[{post.shortcode}] [{post.owner_username}] AI client returned no events for post"
                    )
                    continue

                source_url = f"https://www.instagram.com/p/{post.shortcode}/"
                for idx, event_data in enumerate(extracted_list):
                    added_to_db = None
                    try:
                        logger.debug(
                            f"[{post.shortcode}] [{post.owner_username}] Event {idx + 1}/{len(extracted_list)}: {json.dumps(event_data, ensure_ascii=False, separators=(',', ':'))}"
                        )

                        if not (
                            event_data.get("title")
                            and event_data.get("location")
                            and event_data.get("occurrences")
                            and event_data.get("occurrences")
                        ):
                            missing_fields = []
                            if not event_data.get("title"):
                                missing_fields.append("title")
                            if not event_data.get("location"):
                                missing_fields.append("location")
                            if not event_data.get("occurrences"):
                            if not event_data.get("occurrences"):
                                missing_fields.append("occurrences")
                            logger.warning(
                                f"[{post.shortcode}] [{post.owner_username}] Missing required fields for event '{event_data.get('title', 'Unknown')}': {missing_fields}, skipping"
                            )
                            added_to_db = "missing_fields"
                            continue

                        first_occurrence = event_data.get("occurrences")[0]
                        first_occurrence = event_data.get("occurrences")[0]
                        dtstart_utc = first_occurrence.get("start_utc")
                        now = timezone.now()
                        if isinstance(dtstart_utc, str):
                            dtstart_utc = parser.parse(dtstart_utc)
                            if timezone.is_naive(dtstart_utc):
                                dtstart_utc = timezone.make_aware(dtstart_utc)
                        if dtstart_utc and dtstart_utc < now:
                            logger.info(
                                f"[{post.shortcode}] [{post.owner_username}] Skipping event '{event_data.get('title')}' with past date {dtstart_utc}"
                            )
                            added_to_db = "past_date"
                            continue

                        result = insert_event_to_db(event_data, post.owner_username, source_url)
                        if result is True:
                            events_added += 1
                            logger.info(
                                f"[{post.shortcode}] [{post.owner_username}] Successfully added event '{event_data.get('title')}'"
                            )
                            added_to_db = "success"
                        elif result == "duplicate":
                            logger.warning(
                                f"[{post.shortcode}] [{post.owner_username}] Duplicate event, not added: '{event_data.get('title')}'"
                            )
                            added_to_db = "duplicate"
                        else:
                            logger.error(
                                f"[{post.shortcode}] [{post.owner_username}] Failed to add event '{event_data.get('title')}'"
                            )
                            added_to_db = "failed"
                    except Exception as inner_e:
                        logger.error(
                            f"[{post.shortcode}] [{post.owner_username}] Error handling extracted event index {idx}: {inner_e!s}"
                        )
                        added_to_db = "error"
                    finally:
                        append_event_to_csv(
                            event_data,
                            post.owner_username,
                            source_url,
                            added_to_db=added_to_db or "unknown",
                        )
                posts_processed += 1
                time.sleep(random.uniform(30, 60))

            except Exception as e:
                logger.error(
                    f"[{post.shortcode}] [{post.owner_username}] Error processing post: {e!s}"
                )
                logger.error(f"[{post.shortcode}] [{post.owner_username}] Traceback: {traceback.format_exc()}")
                time.sleep(random.uniform(3, 8))
                continue
            finally:
                IgnoredPost.objects.get_or_create(shortcode=post.shortcode)
                if consec_old_posts >= max_consec_old_posts:
                    termination_reason = (
                        f"reached_consecutive_old_posts={max_consec_old_posts}"
                    )
                    logger.info(
                        f"Reached {max_consec_old_posts} consecutive old posts, stopping."
                    )
                    break
                if check_post_limit():
                    break

        if not termination_reason:
            termination_reason = "no_more_posts"

    except Exception as e:
        # Top-level errors (e.g., loader failure / auth)
        termination_reason = "error"
        logger.error(f"Feed processing aborted due to error: {e!s}")
        logger.error(f"Traceback: {traceback.format_exc()}")

    logger.debug(
        f"Feed processing completed. reason={termination_reason}, posts_processed={posts_processed}, events_added={events_added}"
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
    L.context.request_timeout = 120
    L.context.max_connection_attempts = 5
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
    if L:
        logger.info("Session created successfully!")
        process_recent_feed(L)
    else:
        logger.critical("Failed to initialize Instagram session, stopping...")
