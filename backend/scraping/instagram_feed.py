import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
django.setup()

import csv
import logging
import random
import subprocess
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from instaloader import Instaloader

from example.embedding_utils import is_duplicate_event, find_similar_events
from example.models import Clubs, Events
from services.openai_service import extract_events_from_caption, generate_embedding
from django.db import connection
from services.storage_service import upload_image_from_url

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
]

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "scraping.log"

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

MAX_POSTS = 50
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
                "embedding": embedding or "",
            }
        )


def insert_event_to_db(event_data, club_ig, post_url):
    # Check if an event already exists in db and insert it if not
    event_name = event_data.get("name")  # .title()
    event_date = event_data.get("date")
    event_location = event_data.get("location")  # .title()
    try:
        # Get club_type based on club handle
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
                embedding, threshold=0.90, limit=10, min_date=event_date
            )
            candidate_ids = [row["id"] for row in similar_events]
            if candidate_ids:
                for existing in Events.objects.filter(id__in=candidate_ids, date=event_date):
                    if (
                        (existing.location or "") == (event_location or "")
                        and (existing.start_time or "") == (event_data.get("start_time") or "")
                        and (
                            (existing.end_time or None)
                            == (event_data.get("end_time") or None)
                        )
                    ):
                        logger.info(
                            f"Deleting older duplicate event id={existing.id} before inserting refreshed version"
                        )
                        existing.delete()
        except Exception as dedup_err:
            logger.error(f"Duplicate check via utility failed: {dedup_err}")

        Events.objects.create(
            club_handle=club_ig,
            url=post_url,
            name=event_name,
            date=event_date,
            start_time=event_data["start_time"],
            end_time=event_data["end_time"] or None,
            location=event_location,
            price=event_data.get("price", None),
            food=event_data.get("food") or "",
            registration=bool(event_data.get("registration", False)),
            image_url=event_data.get("image_url"),
            description=event_data.get("description") or "",
            embedding=embedding,
            club_type=club_type,
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
            return False
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
            logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def get_seen_shortcodes():
    """Fetches all post shortcodes from events table in DB"""
    logger.info("Fetching seen shortcodes from the database...")
    try:
        events = Events.objects.filter(url__isnull=False).values_list("url", flat=True)
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

            # Process each event returned by the AI
            for event_data in events_data:
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


@handle_instagram_errors
def session():
    L = Instaloader(user_agent=random.choice(USER_AGENTS))
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
    logger.info("Attemping to load Instagram session...")
    L = session()
    if L:
        logger.info("Session created successfully!")
        process_recent_feed(L)
        
        # Generate recommended filters after processing feed
        logger.info("Generating recommended filters from upcoming events...")
        try:
            script_path = Path(__file__).resolve().parent.parent / "scripts" / "generate_recommended_filters.py"
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                logger.info("✅ Recommended filters generated successfully")
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
            else:
                logger.error(f"❌ Failed to generate recommended filters: {result.stderr}")
        except Exception as e:
            logger.error(f"Error running filter generation script: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    else:
        logger.critical("Failed to initialize Instagram session, stopping...")
