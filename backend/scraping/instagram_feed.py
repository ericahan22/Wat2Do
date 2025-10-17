import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()
from django.db import connection, close_old_connections, OperationalError, ProgrammingError
from django.core.exceptions import FieldDoesNotExist
from django.utils import timezone as django_timezone

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

    tables = _db_table_names()
    try:
        if "events_event" in tables:
            close_old_connections()
            candidates = Events.objects.filter(dtstart__date=event_date)
            for c in candidates:
                c_name = normalize_string(getattr(c, "title", "") or getattr(c, "name", ""))
                c_loc = normalize_string(getattr(c, "location", "") or "")
                if c_name == name and c_loc == location:
                    return True
            return False
        elif "events" in tables:
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT name, location FROM public.events WHERE date = %s", [event_date]
                )
                for row in cur.fetchall():
                    c_name, c_loc = row[0], row[1] or ""
                    if normalize_string(c_name) == name and normalize_string(c_loc) == location:
                        return True
            return False
        else:
            return False
    except (ProgrammingError, OperationalError) as db_err:
        logger.error(f"Database error during duplicate check (table missing or DB down): {db_err}")
        return False
    except Exception as e:
        logger.error(f"Database error during duplicate check: {e!s}")
        return False


def _insert_legacy_event_sql(create_kwargs):
    """Insert into legacy public.events table via raw SQL."""
    sql = """
    INSERT INTO public.events
      (club_handle, url, name, date, start_time, end_time, location,
       price, food, registration, image_url, description, embedding,
       added_at, club_type, reactions, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    vals = [
        create_kwargs.get("club_handle"),
        create_kwargs.get("url"),
        create_kwargs.get("name"),
        create_kwargs.get("date"),
        create_kwargs.get("start_time"),
        create_kwargs.get("end_time"),
        create_kwargs.get("location"),
        create_kwargs.get("price"),
        create_kwargs.get("food"),
        create_kwargs.get("registration", False),
        create_kwargs.get("image_url"),
        create_kwargs.get("description"),
        create_kwargs.get("embedding"),
        create_kwargs.get("added_at"),
        create_kwargs.get("club_type"),
        create_kwargs.get("reactions") or {},
        create_kwargs.get("notes"),
    ]
    with connection.cursor() as cur:
        cur.execute(sql, vals)
        row = cur.fetchone()
        return row[0] if row else None


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
    
    # Parse event_date for dedup and ORM
    event_date = None
    dtstart_obj = None
    dtend_obj = None
    try:
        event_date = datetime.strptime(date, "%Y-%m-%d").date() if date else None
    except Exception:
        event_date = None
    try:
        tz = django_timezone.get_current_timezone() or django_timezone.utc
    except Exception:
        tz = django_timezone.utc
    try:
        if event_date:
            # parse start_time/end_time like "HH:MM"
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(f"{date}T{start_time}")
                except Exception:
                    hh, mm = (start_time.split(":") + ["00"])[:2]
                    start_dt = datetime(event_date.year, event_date.month, event_date.day, int(hh), int(mm))
            else:
                start_dt = datetime(event_date.year, event_date.month, event_date.day, 0, 0)

            if end_time:
                try:
                    end_dt = datetime.fromisoformat(f"{date}T{end_time}")
                except Exception:
                    hh, mm = (end_time.split(":") + ["00"])[:2]
                    end_dt = datetime(event_date.year, event_date.month, event_date.day, int(hh), int(mm))
            else:
                end_dt = start_dt + timedelta(hours=1)

            if django_timezone.is_naive(start_dt):
                dtstart_obj = django_timezone.make_aware(start_dt, timezone=tz)
            else:
                dtstart_obj = start_dt.astimezone(tz)

            if django_timezone.is_naive(end_dt):
                dtend_obj = django_timezone.make_aware(end_dt, timezone=tz)
            else:
                dtend_obj = end_dt.astimezone(tz)
    except Exception:
        dtstart_obj = None
        dtend_obj = None
 
    try:
        # Duplicate check (legacy)
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

        embedding = generate_embedding(event_data.get("description", ""))

        use_dtstart = True
        try:
            Events._meta.get_field("dtstart")
        except FieldDoesNotExist:
            use_dtstart = False
            
        try:
            # Pass event date as min_date to filter out past events first for performance
            similar_events = find_similar_events(
                embedding, threshold=0.90, limit=10, min_date=event_date
            )
            candidate_ids = [row["id"] for row in similar_events]
            if candidate_ids and event_date:
                if use_dtstart:
                    qs = Events.objects.filter(id__in=candidate_ids, dtstart__date=event_date)
                else:
                    qs = Events.objects.filter(id__in=candidate_ids, date=event_date)
                
                for existing in qs:
                    # Only replace if new event has image but existing doesn't,
                    # or if new description is longer (more info)
                    new_img = image_url
                    old_img = getattr(existing, "source_image_url", None) or getattr(existing, "image_url", None)
                    new_desc = description or ""
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
    except Exception as e:
        logger.error(f"Unexpected error finding duplicates: {e}")
        
    create_kwargs = {
        "club_handle": club_ig,
        "url": post_url,
        "name": event_name,
        "date": event_date,  # Python date
        "start_time": start_time or None,
        "end_time": end_time or None,
        "location": location,
        "price": price,
        "food": food,
        "registration": registration,
        "image_url": image_url or None,
        "description": description,
        "embedding": embedding,
        "added_at": None,
        "club_type": club_type,
        "reactions": {},
        "notes": None,
    }

    tables = _db_table_names()
    try:
        if "events_event" in tables:
            Events.objects.create(
                ig_handle=club_ig,
                source_url=post_url,
                title=event_name,
                dtstart=dtstart_obj or None,
                dtend=dtend_obj or None,
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
            return True
        elif "events" in tables:
            new_id = _insert_legacy_event_sql(create_kwargs)
            if new_id:
                logger.info(f"Inserted legacy event id={new_id}")
                append_event_to_csv(event_data, club_ig, post_url, status="success", embedding=embedding)
                return True
            else:
                logger.error("Legacy SQL insert failed (no id returned)")
                append_event_to_csv(event_data, club_ig, post_url, status="failed_sql")
                return False
        else:
            logger.error("No events table available to insert")
            append_event_to_csv(event_data, club_ig, post_url, status="no_table", embedding=embedding)
            return False
    except (ProgrammingError, OperationalError) as db_err:
        logger.error(f"Database error (table/field mismatch or DB down): {db_err}")
        append_event_to_csv(event_data, club_ig, post_url, status="db_unavailable", embedding=embedding)
        return False
    except Exception as e:
        logger.exception(f"Unexpected error inserting event: {e}")
        return False


def _db_table_names():
    try:
        return set(connection.introspection.table_names())
    except Exception:
        return set()
    

def get_seen_shortcodes():
    """Fetches all post shortcodes from events table in DB"""
    logger.info("Fetching seen shortcodes from the database...")
    tables = _db_table_names()
    try:
        if "events_event" in tables:
            events = Events.objects.filter(source_url__isnull=False).values_list("source_url", flat=True)
            shortcodes = {url.split("/")[-2] for url in events if url}
            return shortcodes
        elif "events" in tables:
            with connection.cursor() as cur:
                cur.execute("SELECT url FROM public.events WHERE url IS NOT NULL")
                rows = cur.fetchall()
                shortcodes = {row[0].split("/")[-2] for row in rows if row and row[0]}
                return shortcodes
        else:
            logger.warning("No events table found; treating all posts as unseen")
            return set()
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
    logger.debug(f"Zyte proxy config: proxy={zyte_proxy!r}, cert={zyte_cert_path!s}")
    
    if not zyte_proxy:
        logger.warning("ZYTE_PROXY not set - skipping proxied geolocation test and trying direct request")
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
            proxies={"http": zyte_proxy, "https": zyte_proxy}
        )
        resp.raise_for_status()
        data = resp.json()
        logger.debug(f"Connected via Zyte proxy")
        logger.debug(f"Public IP: {data.get('ip')}")
        logger.debug(f"Country: {data.get('country_name')} ({data.get('country')})")
        logger.debug(f"City: {data.get('city')}")
    except Exception as e:
        logger.warning(f"Proxied geolocation failed: {e!s}")
    return True


@handle_instagram_errors
def session():
    L = Instaloader(user_agent=random.choice(USER_AGENTS))
    try:
        SESSION_CACHE_DIR = Path(os.getenv("GITHUB_WORKSPACE", ".")) / ".insta_cache"
        SESSION_CACHE_DIR.mkdir(exist_ok=True)
        files = [p for p in SESSION_CACHE_DIR.iterdir() if p.is_file()]
        if files:
            session_file = files[0]
        else:
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
