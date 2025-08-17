from instaloader import *
from dotenv import load_dotenv
import os
import csv
from ai_client import parse_caption_for_event
from datetime import datetime, timedelta, timezone
import psycopg2
import logging
import traceback
from datetime import datetime
import sys
from fuzzywuzzy import fuzz


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/scraping.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

def handle_instagram_errors(func):
    # Handle common Instagram errors?
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if any(kw in error_msg for kw in ['login', 'csrf', 'session', 'unauthorized', 'forbidden']):
                logger.error("--- Instagram auth error ---")
                logger.error("Try refreshing CSRF token and/or session ID, update secrets")
                logger.error("----------------------------")
            logger.error(f"Full error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    return wrapper


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


def update_event_csv(event_data, club_name, url):
    """
    Update the event_info.csv file with new event data. 
    """
    csv_file = "event_info.csv" 

    required_fields = ["name", "date", "start_time", "location"]

    for field in required_fields:
        if not event_data.get(field, "").strip():
            print(f"Event missing required field: {field}, skipping...")
            return False

    event_data["club_name"] = club_name
    event_data["url"] = url
    # Append the event data
    with open(csv_file, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "club_name",
            "url",
            "name",
            "date",
            "start_time",
            "end_time",
            "location",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the event data
        event_row = {k: v for k, v in event_data.items()}
        writer.writerow(event_row)

        print(f"Added event: {event_data.get('name')}")
        return True


def process_instagram_posts(max_posts=10):
    """
    Process Instagram posts and extract event information.
    """
    club_name = "uw.wealthmanagement"

    profile = Profile.from_username(L.context, club_name)
    events_added = 0

    for i, post in enumerate(profile.get_posts()):
        if i >= max_posts:
            break

        print(f"\n--- Processing post {i+1} ---")

        if post.caption:
            print(f"Caption: {post.caption[:100]}...")

            # Parse caption using AI client
            event_data = parse_caption_for_event(post.caption)

            # Update CSV if it's an event
            if update_event_csv(event_data, club_name, post.url):
                events_added += 1
        else:
            print("No caption found, skipping...")

    print(f"\n--- Summary ---")
    print(f"Processed {max_posts} posts")
    print(f"Added {events_added} events to CSV")


def insert_event_to_db(event_data, club_ig, post_url, sim_threshold=80):
    # Check if an event already exists in db and insert it if not
    event_name = event_data.get("name").lower()
    event_date = event_data.get("date")
    event_location = event_data.get("location").lower()
    conn = None
    try:
        conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
        cur = conn.cursor()
        
        # Check duplicates
        logger.debug(f"Checking for duplicates: {event_data}")
        query = "SELECT name, location FROM events WHERE date = %s"
        cur.execute(query, (event_date,))
        existing_events = cur.fetchall()
        for existing_name, existing_location in existing_events:
            existing_name = existing_name.lower()
            existing_location = existing_location.lower()
            
            # Check similarity
            name_sim = fuzz.ratio(event_name, existing_name)
            location_sim = fuzz.ratio(event_location, existing_location)
            if name_sim >= sim_threshold and location_sim >= sim_threshold:
                logger.debug(f"Duplicate event found: {existing_name} at {existing_location}")
                return False
            
        insert_query = """
        INSERT INTO events (club_handle, url, name, date, start_time, end_time, location)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """
        cur.execute(insert_query, (
            club_ig,
            post_url,
            event_name,
            event_date,
            event_data["start_time"],
            event_data["end_time"] or None,
            event_location,
        ))
        conn.commit()
        logger.debug(f"Event inserted: {event_data.get('name')} from {club_ig}")
        return True
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        logger.error(f"Event data: {event_data}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        if conn:
            conn.close()


def process_recent_feed(cutoff=datetime.now(timezone.utc) - timedelta(days=1), max_posts=100, max_consec_old_posts=10):
    # Process Instagram feed posts and extract event info. Stops
    #   scraping once posts become older than cutoff.
    try:
        logger.info(f"Starting feed processing with cutoff: {cutoff}")
        events_added = 0
        posts_processed = 0
        consec_old_posts = 0
        for post in L.get_feed_posts():
            try:
                posts_processed += 1
                logger.info("\n" + "-" * 50)
                logger.info(f"Processing post: {post.shortcode} by {post.owner_username}")
                post_time = post.date_utc.replace(tzinfo=timezone.utc)
                if post_time < cutoff:
                    consec_old_posts += 1
                    logger.debug(f"Post {post.shortcode} is older than cutoff ({post_time}), consecutive old posts: {consec_old_posts}")
                    if consec_old_posts >= max_consec_old_posts:
                        logger.info(f"Reached {max_consec_old_posts} consecutive old posts, stopping.")
                        break
                    continue # to next post
                consec_old_posts = 0
                if posts_processed >= max_posts:
                    logger.info(f"Reached max post limit of {max_posts}, stopping.")
                    break

                if post.caption:
                    event_data = parse_caption_for_event(post.caption)
                    if event_data is None:
                        logger.warning(f"AI client returned None for post {post.shortcode}")
                        continue
                    post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                    if event_data.get("name") and event_data.get("date") and event_data.get("location") and event_data.get("start_time"):
                        if insert_event_to_db(event_data, post.owner_username, post_url):
                            events_added += 1
                            logger.info(f"Successfully added event from {post.owner_username}")
                    else:
                        missing_fields = [key for key in ['name', 'date', 'location', 'start_time'] if not event_data.get(key)]
                        logger.warning(f"Missing required fields: {missing_fields}, skipping event")
                else:
                    logger.debug(f"No caption for post {post.shortcode}, skipping...")
                    print("No caption found, skipping...")
            except Exception as e:
                logger.error(f"Error processing post {post.shortcode} by {post.owner_username}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                continue # with next post
        print(f"\n--- Summary ---")
        print(f"Added {events_added} event(s) to Supabase")
        logger.info(f"Feed processing completed. Processed {posts_processed} posts, added {events_added} events")
    except Exception as e:
        logger.error(f"Error in process_recent_feed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


@handle_instagram_errors
def session():
    L = Instaloader()
    try:
        logger.info("Attemping to load Instagram session...")
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
    # process_instagram_posts(max_posts=10)
    L = session()
    process_recent_feed()