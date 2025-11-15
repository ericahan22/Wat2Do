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

from django.utils import timezone
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

from apps.clubs.models import Clubs
from apps.events.models import EventDates, Events, IgnoredPost
from scraping.logging_config import logger
from scraping.zyte_setup import setup_zyte
from services.openai_service import (
    extract_events_from_caption,
)
from services.storage_service import upload_image_from_url
from utils.date_utils import parse_utc_datetime
from utils.scraping_utils import (
    jaccard_similarity,
    normalize,
    sequence_similarity,
)


MAX_POSTS = int(os.getenv("MAX_POSTS", "15"))
MAX_CONSEC_OLD_POSTS = 10
CUTOFF_DAYS = int(os.getenv("CUTOFF_DAYS", "2"))

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

# Get credentials from environment variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SESSIONID = os.getenv("SESSIONID")


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
        event_shortcodes = {url.split("/")[-2] for url in events if url}
        ignored_shortcodes = set(
            IgnoredPost.objects.values_list("shortcode", flat=True)
        )
        shortcodes = event_shortcodes | ignored_shortcodes
        return shortcodes
    except Exception as e:
        logger.error(f"Could not fetch shortcodes from database: {e}")
        return set()


def process_recent_feed(
    cl,
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

    try:
        posts_iterator = cl.get_timeline_feed()
        logger.info(f"Fetched {len(posts_iterator)} posts from timeline feed.")

        for post in posts_iterator:
            try:
                post_time = post.taken_at
                post_shortcode = post.code
                post_username = post.user.username

                if post_time < cutoff:
                    consec_old_posts += 1
                    logger.debug(
                        f"[{post_shortcode}] [{post_username}] Skipping old post; consec_old_posts={consec_old_posts}"
                    )
                    continue
                if post_shortcode in seen_shortcodes:
                    logger.debug(
                        f"[{post_shortcode}] [{post_username}] Skipping previously seen post"
                    )
                    continue

                consec_old_posts = 0
                logger.info("-" * 100)
                logger.info(
                    f"[{post_shortcode}] [{post_username}] Processing post"
                )

                raw_image_url = None
                if post.media_type == 8 and post.resources:  # Carousel
                    raw_image_url = post.resources[0].thumbnail_url
                elif post.thumbnail_url:  # Single photo or video thumbnail
                    raw_image_url = post.thumbnail_url
                if raw_image_url:
                    time.sleep(random.uniform(1, 3))
                    source_image_url = upload_image_from_url(str(raw_image_url))
                    logger.debug(
                        f"[{post_shortcode}] [{post_username}] Uploaded image to S3: {source_image_url}"
                    )
                else:
                    logger.warning(
                        f"[{post_shortcode}] [{post_username}] No image URL found for post, skipping image upload"
                    )
                    source_image_url = None

                extracted_list = extract_events_from_caption(
                    post.caption_text, source_image_url, post.taken_at
                )
                if not extracted_list:
                    logger.warning(
                        f"[{post_shortcode}] [{post_username}] AI client returned no events for post"
                    )
                    continue

                source_url = f"https://www.instagram.com/p/{post_shortcode}/"
                for idx, event_data in enumerate(extracted_list):
                    added_to_db = None
                    try:
                        logger.debug(
                            f"[{post_shortcode}] [{post_username}] Event {idx + 1}/{len(extracted_list)}: {json.dumps(event_data, ensure_ascii=False, separators=(',', ':'))}"
                        )

                        if not (
                            event_data.get("title")
                            and event_data.get("location")
                            and event_data.get("occurrences")
                        ):
                            missing_fields = []
                            if not event_data.get("title"):
                                missing_fields.append("title")
                            if not event_data.get("location"):
                                missing_fields.append("location")
                            if not event_data.get("occurrences"):
                                missing_fields.append("occurrences")
                            logger.warning(
                                f"[{post_shortcode}] [{post_username}] Missing required fields for event '{event_data.get('title', 'Unknown')}': {missing_fields}, skipping"
                            )
                            added_to_db = "missing_fields"
                            continue

                        first_occurrence = event_data.get("occurrences")[0]
                        dtstart_utc = first_occurrence.get("dtstart_utc")
                        now = timezone.now()
                        if isinstance(dtstart_utc, str):
                            dtstart_utc = parse_utc_datetime(dtstart_utc)
                        if dtstart_utc and dtstart_utc < now:
                            logger.info(
                                f"[{post_shortcode}] [{post_username}] Skipping event '{event_data.get('title')}' with past date {dtstart_utc}"
                            )
                            added_to_db = "past_date"
                            continue

                        result = insert_event_to_db(
                            event_data, post_username, source_url
                        )
                        if result is True:
                            events_added += 1
                            logger.info(
                                f"[{post_shortcode}] [{post_username}] Successfully added event '{event_data.get('title')}'"
                            )
                            added_to_db = "success"
                        elif result == "duplicate":
                            logger.warning(
                                f"[{post_shortcode}] [{post_username}] Duplicate event, not added: '{event_data.get('title')}'"
                            )
                            added_to_db = "duplicate"
                        else:
                            logger.error(
                                f"[{post_shortcode}] [{post_username}] Failed to add event '{event_data.get('title')}'"
                            )
                            added_to_db = "failed"
                    except Exception as inner_e:
                        logger.error(
                            f"[{post_shortcode}] [{post_username}] Error handling extracted event index {idx}: {inner_e!s}"
                        )
                        added_to_db = "error"
                    finally:
                        append_event_to_csv(
                            event_data,
                            post_username,
                            source_url,
                            added_to_db=added_to_db or "unknown",
                        )

            except Exception as e:
                logger.error(
                    f"[{post_shortcode}] [{post_username}] Error processing post: {e!s}"
                )
                logger.error(
                    f"[{post_shortcode}] [{post_username}] Traceback: {traceback.format_exc()}"
                )
                time.sleep(random.uniform(3, 8))
                continue
            finally:
                posts_processed += 1
                IgnoredPost.objects.get_or_create(shortcode=post_shortcode)
                
                if posts_processed > max_posts:
                    termination_reason = f"reached_max_posts={max_posts}"
                    logger.info(f"Reached max post limit of {max_posts}, stopping.")
                    break
                if consec_old_posts >= max_consec_old_posts:
                    termination_reason = (
                        f"reached_consecutive_old_posts={max_consec_old_posts}"
                    )
                    logger.info(
                        f"Reached {max_consec_old_posts} consecutive old posts, stopping."
                    )
                    break
                
            time.sleep(random.uniform(30, 90))

        if not termination_reason:
            termination_reason = "no_more_posts"

    except LoginRequired:
        logger.warning("LoginRequired exception caught in process_recent_feed. Re-raising.")
        raise
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


def get_session_file_path():
    """Helper function to get the consistent session file path"""
    try:
        SESSION_CACHE_DIR = Path(os.getenv("GITHUB_WORKSPACE", ".")) / ".insta_cache"
        SESSION_CACHE_DIR.mkdir(exist_ok=True)
        session_file = SESSION_CACHE_DIR / f"{USERNAME}_session.json"
    except Exception:
        session_file = Path(__file__).resolve().parent.parent / f"{USERNAME}_session.json"
    return session_file


def session():
    """
    Creates an instagrapi Client, injects the Zyte proxied session,
    and loads the session from file or environment variables.
    """
    zyte_cert_path = setup_zyte()
    zyte_proxy = os.getenv("ZYTE_PROXY")
    if not zyte_proxy:
        logger.critical("ZYTE_PROXY not set, aborting...")
        return None
    
    session_file = get_session_file_path()
    session_data = None
    if session_file.exists():
        try:
            session_data = json.loads(session_file.read_text())
            logger.info(f"Manually loaded session from file: {session_file!s}")
        except Exception as e:
            logger.warning(f"Could not read session file: {e}, will re-login")
            session_file.unlink()
    
    client_settings = {
        "proxy": zyte_proxy,
        "request_timeout": 30,
        "delay_range": [1, 3]
    }
    if session_data:
        client_settings["settings"] = session_data

    try:
        cl = Client(**client_settings)
        cl.public.verify = str(zyte_cert_path)
        cl.private.verify = str(zyte_cert_path)
        zyte_headers = {
            "Zyte-Override-Headers": "User-Agent",
            "Zyte-Geolocation": "CA"
        }
        cl.public.headers.update(zyte_headers)
        cl.private.headers.update(zyte_headers)
        logger.debug("Zyte proxy/SSL/headers configured on client sessions.")   

        if session_data:
            cl.user_id = session_data["user_id"]
            logger.debug("Validating session...")
            cl.user_info_v1(cl.user_id)
            logger.info("Successfully loaded and validated session")
        else:
            logger.info("No session file found, logging in with SESSIONID")
            if not SESSIONID:
                raise ValueError("SESSIONID not found in .env, cannot login.")
            cl.login_by_sessionid(SESSIONID)
            logger.info("Logged in using SESSIONID.")
            cl.dump_settings(session_file)
        return cl

    except LoginRequired:
        logger.warning("Invalid session, attempting full login with USERNAME/PASSWORD")
        try:
            if not USERNAME or not PASSWORD:
                raise ValueError("USERNAME/PASSWORD not found in .env, cannot re-login")
            cl = Client(**client_settings)
            cl.public.verify = str(zyte_cert_path)
            cl.private.verify = str(zyte_cert_path)
            cl.public.headers.update(zyte_headers)
            cl.private.headers.update(zyte_headers)
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(session_file)
            logger.info("Logged in successfully with username/password")
            return cl
        except Exception as login_e:
            logger.error(f"Full login with USERNAME/PASSWORD failed: {login_e}")
            logger.error(traceback.format_exc())
            return None   
    except Exception as e:
        logger.error(f"Failed to initialize session: {e}")
        logger.error(traceback.format_exc())
        return None


if __name__ == "__main__":
    lock_file_path = Path(__file__).parent / "scrape.lock"
    if lock_file_path.exists():
        sys.exit()
    try:
        lock_file_path.touch()
        logger.info("Attemping to load Instagram session...")
        cl = session()
        if not cl:
            logger.critical("Failed to initialize Instagram session (likely Zyte proxy failure), stopping...")
            sys.exit()
        logger.info("Session object created, attempting to process feed...")
        process_recent_feed(cl)
        logger.info("Session created/validated and feed processed successfully!")
    except Exception as e:
        logger.error(f"An uncaught exception occurred: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        if lock_file_path.exists():
            lock_file_path.unlink()
