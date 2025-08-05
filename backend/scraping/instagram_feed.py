from instaloader import *
from dotenv import load_dotenv
import os
import csv
from ai_client import parse_caption_for_event
from datetime import datetime, timedelta, timezone
import psycopg2

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


def insert_event_to_db(event_data, club_ig, post_url):
    conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
    cur = conn.cursor()
    query = """
    INSERT INTO events (club_handle, url, name, date, start_time, end_time, location)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING;
    """
    cur.execute(query, (
        club_ig,
        post_url,
        event_data["name"],
        event_data["date"],
        event_data["start_time"],
        event_data["end_time"] or None,
        event_data["location"],
    ))
    conn.commit()
    cur.close()
    conn.close()
    return True


def process_recent_feed(cutoff=datetime.now(timezone.utc) - timedelta(days=1)):
    events_added = 0
    for post in L.get_feed_posts():
        post_time = post.date_utc.replace(tzinfo=timezone.utc)
        if post_time >= cutoff:
            # print(post.date_utc, post.shortcode, post.owner_username)
            print(f"\n--- Processing post ---")
            if post.caption:
                print(f"Caption: {post.caption[:100]}...")
                event_data = parse_caption_for_event(post.caption)
                post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                if update_event_csv(event_data, post.owner_username, post_url):
                    if insert_event_to_db(event_data, post.owner_username, post_url):
                        events_added += 1
            else:
                print("No caption found, skipping...")

    print(f"\n--- Summary ---")
    print(f"Added {events_added} event(s) to Supabase")


def session():
    L = Instaloader()
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
        print("Successfully logged in")
        return L
    except Exception as e:
        print(f"Failed to load session: {e}")
        raise


if __name__ == "__main__":
    # process_instagram_posts(max_posts=10)
    L = session()
    process_recent_feed()