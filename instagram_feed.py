from instaloader import *
from dotenv import load_dotenv
import os
import csv
from ai_client import parse_caption_for_event

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
    L = Instaloader()
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


if __name__ == "__main__":
    process_instagram_posts(max_posts=10)
