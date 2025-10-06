import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
django.setup()

import csv
import logging
import traceback
from pathlib import Path
from example.embedding_utils import is_duplicate_event
from example.models import Clubs, Events
from services.openai_service import generate_embedding


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "scraping.log"

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

MAX_POSTS = 100
MAX_CONSEC_OLD_POSTS = 10
CUTOFF_DAYS = 2


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


def insert_event_to_db(event_data, club_ig, post_url, image_url):
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

        # Check duplicates
        if is_duplicate_event(event_data):
            logger.debug(f"Duplicate event found: {event_data.get('name')} at {event_data.get('location')}")
            return False

        # Generate embedding
        embedding = generate_embedding(event_data.get("description", ""))

        # Create event using Django ORM
        Events.objects.create(
            club_handle=club_ig,
            url=post_url,
            name=event_data.get("name"),
            date=event_data.get("date"),
            start_time=event_data.get("start_time"),
            end_time=event_data.get("end_time"),
            location=event_data.get("location"),
            price=event_data.get("price", None),
            food=event_data.get("food") or "",
            registration=bool(event_data.get("registration", False)),
            image_url=image_url,
            description=event_data.get("description") or "",
            embedding=embedding,
            club_type=club_type,
        )
        logger.info(f"Event inserted: {event_data.get('name')} from {club_ig}")
        # append_event_to_csv(
        #     event_data, club_ig, post_url, status="success", embedding=embedding
        # )
        return True
    except Exception as e:
        logger.error(f"Database insertion failed for event '{event_data.get('name')}': {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        embedding = generate_embedding(event_data.get("description", ""))
        # append_event_to_csv(
        #     event_data, club_ig, post_url, status="failed", embedding=embedding
        # )
        return False


def get_seen_shortcodes():
    """Fetches all post shortcodes from events table in DB"""
    logger.info("Fetching seen shortcodes from the database...")
    try:
        urls = Events.objects.filter(url__isnull=False).values_list("url", flat=True)
        shortcodes = {url.split("/")[-2] for url in urls if "/p/" in url}
        return shortcodes
    except Exception as e:
        logger.error(f"Could not fetch shortcodes from database: {e}")
        return set()
