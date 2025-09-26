import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from instaloader import Instaloader
from dotenv import load_dotenv
import csv
from services.openai_service import extract_event_from_caption
from services.storage_service import upload_image_from_url
from datetime import datetime, timedelta, timezone
import logging
import traceback
import time
from pathlib import Path
from django.db import connection

from example.embedding_utils import generate_event_embedding, is_duplicate_event


logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/scraping.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


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
        if "image_versions2" in post._node and post._node["image_versions2"]:
            return post._node["image_versions2"]["candidates"][0]["url"]

        if "carousel_media" in post._node and post._node["carousel_media"]:
            return post._node["carousel_media"][0]["image_versions2"]["candidates"][0][
                "url"
            ]

        if "display_url" in post._node and post._node["display_url"]:
            return post._node["display_url"]
        return None
    except (KeyError, AttributeError) as e:
        logger.error(
            f"Error accessing image URL for post {getattr(post, 'shortcode', 'unknown')}: {str(e)}"
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
            logger.error(f"Full error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    return wrapper


def append_event_to_csv(event_data, club_ig, post_url, status="success"):
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
            "status",
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
                "status": status,
            }
        )


def insert_event_to_db(event_data, club_ig, post_url):
    # Check if an event already exists in db and insert it if not
    event_name = event_data.get("name")  # .title()
    event_date = event_data.get("date")
    event_location = event_data.get("location")  # .title()
    try:
        with connection.cursor() as cur:
            # Get club_type from club handle
            cur.execute("SELECT club_type FROM clubs WHERE ig = %s", (club_ig,))
            club_row = cur.fetchone()
            club_type = club_row[0] if club_row else None
            if not club_type:
                logger.warning(f"Club with handle {club_ig} not found in clubs. Inserting event with null club_type.")

            # Check duplicates using vector similarity
            logger.debug(f"Checking for duplicates using vector similarity: {event_data}")

            # Check if this event is a duplicate using vector similarity
            if is_duplicate_event(event_data):
                logger.debug(
                    f"Duplicate event found using vector similarity: {event_name} at {event_location}"
                )
                return False

            # Generate embedding for the event
            embedding = generate_event_embedding(event_data)

            insert_query = """
            INSERT INTO events (
                club_handle, url, name, date, start_time, end_time, location, price, food, registration, image_url, embedding, club_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector, %s)
            ON CONFLICT DO NOTHING;
            """
            cur.execute(
                insert_query,
                (
                    club_ig,
                    post_url,
                    event_name,
                    event_date,
                    event_data["start_time"],
                    event_data["end_time"] or None,
                    event_location,
                    event_data.get("price", None),
                    event_data.get("food") or "",
                    bool(event_data.get("registration", False)),
                    event_data.get("image_url"),
                    embedding,
                    club_type,
                ),
            )
            logger.debug(f"Event inserted: {event_data.get('name')} from {club_ig}")

        try:
            append_event_to_csv(event_data, club_ig, post_url, status="success")
            logger.info(f"Appended event to CSV: {event_data.get('name')}")
        except Exception as csv_err:
            logger.error(
                f"Database insert succeeded, but failed to append to CSV: {csv_err}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

        return True
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        logger.error(f"Event data: {event_data}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        try:
            append_event_to_csv(event_data, club_ig, post_url, status="failed")
            logger.info(f"Appended event to CSV: {event_data.get('name')}")
        except Exception as csv_err:
            logger.error(
                f"Database insert failed, and failed to append to CSV: {csv_err}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")

        return False


def process_recent_feed(
    loader,
    cutoff=datetime.now(timezone.utc) - timedelta(days=2),
    max_posts=100,
    max_consec_old_posts=10,
):
    # Process Instagram feed posts and extract event info. Stops
    #   scraping once posts become older than cutoff.
    events_added = 0
    posts_processed = 0
    consec_old_posts = 0
    logger.info(f"Starting feed processing with cutoff: {cutoff}")

    for post in loader.get_feed_posts():
        try:
            posts_processed += 1
            logger.info("\n" + "-" * 50)
            logger.info(f"Processing post: {post.shortcode} by {post.owner_username}")

            post_time = post.date_utc.replace(tzinfo=timezone.utc)
            if post_time < cutoff:
                consec_old_posts += 1
                if consec_old_posts >= max_consec_old_posts:
                    logger.info(
                        f"Reached {max_consec_old_posts} consecutive old posts, stopping."
                    )
                    break
                continue  # to next post
            consec_old_posts = 0

            if posts_processed >= max_posts:
                logger.info(f"Reached max post limit of {max_posts}, stopping.")
                break

            # Safely get image URL and upload to S3
            raw_image_url = get_post_image_url(post)
            if raw_image_url:
                image_url = upload_image_from_url(raw_image_url)
                logger.info(f"Uploaded image to S3: {image_url}")
            else:
                logger.warning(
                    f"No image URL found for post {post.shortcode}, skipping image upload"
                )
                image_url = None

            event_data = extract_event_from_caption(post.caption, image_url)

            if event_data is None:
                logger.warning(f"AI client returned None for post {post.shortcode}")
                continue

            post_url = f"https://www.instagram.com/p/{post.shortcode}/"
            if (
                event_data.get("name")
                and event_data.get("date")
                and event_data.get("location")
                and event_data.get("start_time")
            ):
                if insert_event_to_db(event_data, post.owner_username, post_url):
                    events_added += 1
                    logger.info(f"Successfully added event from {post.owner_username}")
            else:
                missing_fields = [
                    key
                    for key in ["name", "date", "location", "start_time"]
                    if not event_data.get(key)
                ]
                logger.warning(
                    f"Missing required fields: {missing_fields}, skipping event"
                )
                append_event_to_csv(
                    event_data, post.owner_username, post_url, status="missing_fields"
                )
            time.sleep(5)
        except Exception as e:
            logger.error(
                f"Error processing post {post.shortcode} by {post.owner_username}: {str(e)}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")
            continue  # with next post
    logger.info(
        f"Feed processing completed. Processed {posts_processed} posts, added {events_added} events"
    )
    logger.info(f"\n--- Summary ---")
    logger.info(f"Added {events_added} event(s) to Supabase")


@handle_instagram_errors
def session():
    L = Instaloader()
    logger.info("Attemping to load Instagram session...")
    try:
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
        logger.info("Session created successfully")
        return L
    except Exception as e:
        logger.error(f"Failed to load session: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


if __name__ == "__main__":
    L = session()
    process_recent_feed(L)
