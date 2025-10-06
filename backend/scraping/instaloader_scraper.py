import os
import random
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
from instaloader import Instaloader
from scraping.scraping_utils import (
    MAX_CONSEC_OLD_POSTS,
    MAX_POSTS,
    append_event_to_csv,
    get_seen_shortcodes,
    insert_event_to_db,
    logger,
    CUTOFF_DAYS
)
from services.openai_service import extract_events_from_caption, generate_embedding
from services.storage_service import upload_image_from_url


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
]

load_dotenv()

# Get credentials from environment variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
CSRFTOKEN = os.getenv("CSRFTOKEN")
SESSIONID = os.getenv("SESSIONID")
DS_USER_ID = os.getenv("DS_USER_ID")
MID = os.getenv("MID")
IG_DID = os.getenv("IG_DID")


def get_post_image_url(post):
    """Extracts best image from post"""
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
    except (KeyError, AttributeError, IndexError) as e:
        logger.error(
            f"Error accessing image URL for post {getattr(post, 'shortcode', 'unknown')}: {e!s}"
        )
        return None


def handle_instagram_errors(func):
    """Handle common Instagram auth/request errors"""
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
            logger.error(f"Full error: {e!s}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    return wrapper


def process_recent_feed(
    loader,
    cutoff=datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS),
    max_posts=MAX_POSTS,
    max_consec_old_posts=MAX_CONSEC_OLD_POSTS,
):
    """Processes feed, extracts event info, stores in db"""
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
                status = "unknown"
                has_required_fields = (
                    event_data.get("name")
                    and event_data.get("date")
                    and event_data.get("location")
                    and event_data.get("start_time")
                )
                if has_required_fields:
                    if insert_event_to_db(event_data, post.owner_username, post_url, image_url):
                        events_added += 1
                        logger.info(
                            f"Successfully added event '{event_data.get('name')}' from {post.owner_username}"
                        )
                    else:
                        status = "failed"
                        logger.error(
                            f"Failed to add event '{event_data.get('name')}' from {post.owner_username}"
                        )
                else:
                    missing_fields = [
                        key
                        for key in ["name", "date", "location", "start_time"]
                        if not event_data.get(key)
                    ]
                    status = "missing_fields"
                    logger.warning(
                        f"Missing required fields for event '{event_data.get('name', 'Unknown')}': {missing_fields}, skipping event"
                    )
                embedding = generate_embedding(event_data.get("description", ""))
                append_event_to_csv(
                    event_data,
                    post.owner_username,
                    post_url,
                    status=status,
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
    logger.info("Attempting to load Instagram session...")
    L = session()
    if L:
        logger.info("Session created successfully!")
        process_recent_feed(L)
    else:
        logger.critical("Failed to initialize Instagram session, stopping...")
