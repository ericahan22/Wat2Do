import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()
from django.db import close_old_connections

import csv
import random
import time
import traceback
import re
import requests
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from instaloader import Instaloader

from apps.clubs.models import Clubs
from apps.events.models import Events
from services.openai_service import extract_events_from_caption, generate_embedding
from services.storage_service import upload_image_from_url
from zyte_setup import setup_zyte
from logging_config import logger
from utils.embedding_utils import find_similar_events

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
]

MAX_POSTS = int(os.getenv("MAX_POSTS", "100"))
MAX_CONSEC_OLD_POSTS = 10
CUTOFF_DAYS = 2

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


def handle_instagram_errors(func):
    # Handle common Instagram errors?
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if any(
                kw in error_msg
                for kw in ["login", "csrf", "session", "unauthorized", "forbidden"]
            ):
                logger.error("--- Instagram auth error ---")
                logger.error(
                    "Try refreshing CSRF token and/or session ID, update secrets"
                )
                logger.error("----------------------------")
            logger.error(f"Full error: {e!s}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    return wrapper


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
    name = normalize_string(event_data.get("name") or event_data.get("title"))
    location = normalize_string(event_data.get("location"))
    date_str = (event_data.get("date") or "").strip()
    if not date_str:
        return False
    try:
        event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logger.warning(f"Invalid date for duplicate check: '{date_str}'")
        return False

    try:
        close_old_connections()
        candidates = Events.objects.filter(dtstart__date=event_date)
        for c in candidates:
            c_name = normalize_string(getattr(c, "title", "") or "")
            c_loc = normalize_string(getattr(c, "location", "") or "")
            if c_name == name and c_loc == location:
                return True
        return False
    except Exception as e:
        logger.error(f"Database error during duplicate check: {e!s}")
        return False


def append_event_to_csv(
    event_data, club_ig, post_url, status="success", embedding=None
):
    csv_file = Path(__file__).resolve().parent / "events_scraped.csv"
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_file.exists()

    with open(csv_file, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "club_handle",
            "url",
            "name",
            "date",
            "start_time",
            "end_time",
            "location",
            "price",
            "food",
            "registration",
            "image_url",
            "description",
            "status",
            "reactions",
            "embedding",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "club_handle": club_ig,
                "url": post_url,
                "name": event_data.get("name", ""),
                "date": event_data.get("date", ""),
                "start_time": event_data.get("start_time", ""),
                "end_time": event_data.get("end_time", ""),
                "location": event_data.get("location", ""),
                "price": event_data.get("price", ""),
                "food": event_data.get("food", ""),
                "registration": event_data.get("registration", False),
                "image_url": event_data.get("image_url", ""),
                "description": event_data.get("description", ""),
                "status": status,
                "reactions": json.dumps(event_data.get("reactions") or {}),
                "embedding": embedding or "",
            }
        )


def insert_event_to_db(event_data, club_ig, post_url):
    """Map scraped event data to Event model fields, insert to DB"""
    event_name = event_data.get("name") or event_data.get("title") or ""
    date = event_data.get("date") or ""
    start_time = event_data.get("start_time") or ""
    end_time = event_data.get("end_time") or ""
    image_url = event_data.get("image_url") or event_data.get("source_image_url") or ""
    description = event_data.get("description") or ""
    location = event_data.get("location") or ""
    price = event_data.get("price", None)
    food = event_data.get("food", None)
    registration = bool(event_data.get("registration", False))
    
    # Parse dtstart/dtend datetimes for model fields
    try:
        if date and start_time:
            dtstart = datetime.fromisoformat(f"{date}T{start_time}")
        elif date:
            dtstart = datetime.fromisoformat(f"{date}T00:00:00")
        else:
            dtstart = None
        if date and end_time:
            dtend = datetime.fromisoformat(f"{date}T{end_time}")
        else:
            dtend = None
    except Exception:
        dtstart = None
        dtend = None
        
    try:
        # Duplicate check
        if is_duplicate_event(event_data):
            logger.info(
                f"Duplicate event detected, skipping {event_name} on {date} at {location}"
            )
            return False

        # Get club_type based on club handle from Clubs model
        try:
            club = Clubs.objects.get(ig=club_ig)
            club_type = club.club_type
        except Clubs.DoesNotExist:
            club_type = None
            logger.warning(
                f"Club with handle {club_ig} not found, inserting event with null club_type"
            )

        embedding = generate_embedding(event_data["description"])

        try:
            # Pass event date as min_date to filter out past events first for performance
            similar_events = find_similar_events(
                embedding, threshold=0.90, limit=10, min_date=date
            )
            candidate_ids = [row["id"] for row in similar_events]
            if candidate_ids:
                for existing in Events.objects.filter(
                    id__in=candidate_ids, dtstart__date=date
                ):
                    # Only replace if new event has image but existing doesn't,
                    # or if new description is longer (more info)
                    new_img = event_data.get("image_url")
                    old_img = getattr(existing, "source_image_url", getattr(existing, "image_url", None))
                    new_desc = event_data.get("description") or ""
                    old_desc = existing.description or ""
                    if (not old_img and new_img) or (
                        len(new_desc) > len(old_desc) + 10
                    ):
                        logger.info(
                            f"Replacing older event: id={existing.id} with newer one"
                        )
                        existing.delete()
        except Exception as dedup_err:
            logger.error(f"Duplicate check via utility failed: {dedup_err}")

        Events.objects.create(
            ig_handle=club_ig,
            source_url=post_url,
            title=event_name,
            dtstart=dtstart,
            dtend=dtend,
            location=location,
            price=price,
            food=food,
            registration=registration,
            source_image_url=image_url or None,
            description=description,
            embedding=embedding,
            club_type=club_type,
            status="scraped",
        )
        logger.debug(f"Event inserted: {event_data.get('name')} from {club_ig}")
        try:
            append_event_to_csv(
                event_data, club_ig, post_url, status="success", embedding=embedding
            )
            logger.info(f"Appended event to CSV: {event_data.get('name')}")
        except Exception as csv_err:
            logger.error(
                f"Database insert succeeded, but failed to append to CSV: {csv_err}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")
        return True
    except Exception as e:
        logger.error(f"Database error: {e!s}")
        logger.error(f"Event data: {event_data}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        try:
            embedding = generate_embedding(event_data["description"])
            append_event_to_csv(
                event_data, club_ig, post_url, status="failed", embedding=embedding
            )
            logger.info(f"Appended event to CSV: {event_data.get('name')}")
        except Exception as csv_err:
            logger.error(f"Database and CSV inserts failed: {csv_err}")
        return False


def get_seen_shortcodes():
    """Fetches all post shortcodes from events table in DB"""
    logger.info("Fetching seen shortcodes from the database...")
    try:
        events = Events.objects.filter(source_url__isnull=False).values_list("source_url", flat=True)
        shortcodes = {url.split("/")[-2] for url in events if url}
        return shortcodes
    except Exception as e:
        logger.error(f"Could not fetch shortcodes from database: {e}")
        return set()


def process_recent_feed(
    loader,
    cutoff=datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS),
    max_posts=MAX_POSTS,
    max_consec_old_posts=MAX_CONSEC_OLD_POSTS,
):
    # Process Instagram feed posts and extract event info. Stops
    #   scraping once posts become older than cutoff.
    events_added = 0
    posts_processed = 0
    consec_old_posts = 0
    logger.info(f"Starting feed processing with cutoff: {cutoff}")

    seen_shortcodes = get_seen_shortcodes()

    for post in loader.get_feed_posts():
        try:
            post_time = post.date_utc.replace(tzinfo=timezone.utc)
            if post.shortcode in seen_shortcodes or post_time < cutoff:
                consec_old_posts += 1
                if consec_old_posts >= max_consec_old_posts:
                    logger.info(
                        f"Reached {max_consec_old_posts} consecutive old posts, stopping."
                    )
                    break
                continue  # to next post

            consec_old_posts = 0
            posts_processed += 1
            logger.info("\n" + "-" * 50)
            logger.info(f"Processing post: {post.shortcode} by {post.owner_username}")

            # Safely get image URL and upload to S3
            raw_image_url = get_post_image_url(post)
            if raw_image_url:
                time.sleep(random.uniform(1, 3))
                image_url = upload_image_from_url(raw_image_url)
                logger.info(f"Uploaded image to S3: {image_url}")
            else:
                logger.warning(
                    f"No image URL found for post {post.shortcode}, skipping image upload"
                )
                image_url = None

            events_data = extract_events_from_caption(post.caption, image_url)
            if not events_data or len(events_data) == 0:
                logger.warning(
                    f"AI client returned no events for post {post.shortcode}"
                )
                continue

            post_url = f"https://www.instagram.com/p/{post.shortcode}/"
            today = datetime.now(timezone.utc).date()

            # Process each event returned by the AI
            for event_data in events_data:
                date_str = (event_data.get("date") or "").strip()
                if not date_str:
                    logger.warning(
                        f"Skipping event '{event_data.get('name', 'Unknown')}' from post {post.shortcode}: missing date"
                    )
                    continue
                try:
                    event_date = datetime.strptime(event_data.get("date"), "%Y-%m-%d").date()
                except ValueError:
                    logger.warning(
                        f"Skipping event '{event_data.get('name', 'Unkown')}' from post {post.shortcode}: invalid date '{date_str}'"
                    )
                    continue
                if event_date < today:
                    logger.info(
                        f"Skipping event '{event_data.get('name')}' with past date {event_date}"
                    )
                    continue

                if (
                    event_data.get("name")
                    and event_data.get("date")
                    and event_data.get("location")
                    and event_data.get("start_time")
                ):
                    if insert_event_to_db(event_data, post.owner_username, post_url):
                        events_added += 1
                        logger.info(
                            f"Successfully added event '{event_data.get('name')}' from {post.owner_username}"
                        )
                    else:
                        logger.error(
                            f"Failed to add event '{event_data.get('name')}' from {post.owner_username}"
                        )
                else:
                    missing_fields = [
                        key
                        for key in ["name", "date", "location", "start_time"]
                        if not event_data.get(key)
                    ]
                    logger.warning(
                        f"Missing required fields for event '{event_data.get('name', 'Unknown')}': {missing_fields}, skipping event"
                    )
                    embedding = generate_embedding(event_data["description"])
                    append_event_to_csv(
                        event_data,
                        post.owner_username,
                        post_url,
                        status="missing_fields",
                        embedding=embedding,
                    )

            time.sleep(random.uniform(15, 45))

            if posts_processed >= max_posts:
                logger.info(f"Reached max post limit of {max_posts}, stopping")
                break
        except Exception as e:
            logger.error(
                f"Error processing post {post.shortcode} by {post.owner_username}: {e!s}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")
            time.sleep(random.uniform(3, 8))
            continue  # with next post
    logger.info(
        f"Feed processing completed. Processed {posts_processed} posts, added {events_added} events"
    )
    logger.info("\n--- Summary ---")
    logger.info(f"Added {events_added} event(s) to Supabase")


def test_zyte_proxy(country="CA"):
    """
    Patch requests.Session to route through Zyte with geolocation,
    test Zyte proxy routing and geolocation
    """
    zyte_cert_path = setup_zyte()
    zyte_proxy = os.getenv("ZYTE_PROXY")
    os.environ['https_proxy'] = zyte_proxy
    
    old_request = requests.Session.request

    def zyte_request(self, method, url, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Zyte-Geolocation"] = country
        kwargs["headers"] = headers
        kwargs["verify"] = zyte_cert_path
        kwargs["proxies"] = {"http": zyte_proxy, "https": zyte_proxy}
        kwargs["timeout"] = kwargs.get("timeout", 60)
        return old_request(self, method, url, **kwargs)

    requests.Session.request = zyte_request
    
    logger.debug(f"Testing Zyte proxy geolocation: {country}")
    try:
        resp = requests.get(
            "https://ipapi.co/json/",
            timeout=15,
            verify=zyte_cert_path)
        resp.raise_for_status()
        data = resp.json()
        logger.debug(f"Connected via Zyte proxy")
        logger.debug(f"Public IP: {data.get('ip')}")
        logger.debug(f"Country: {data.get('country_name')} ({data.get('country')})")
        logger.debug(f"City: {data.get('city')}")
    except Exception as e:
        print(f"Proxy geolocation test failed: {e}")
        
        
@handle_instagram_errors
def session():
    L = Instaloader(user_agent=random.choice(USER_AGENTS))
    try:
        SESSION_CACHE_DIR = Path(os.getenv("GITHUB_WORKSPACE", ".")) / ".insta_cache"
        SESSION_CACHE_DIR.mkdir(exist_ok=True)
        session_file = SESSION_CACHE_DIR / f"session-{USERNAME}"
    except Exception as e:
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
