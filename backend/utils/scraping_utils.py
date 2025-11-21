import csv
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from django.db import transaction

from utils.date_utils import parse_utc_datetime

from apps.clubs.models import Clubs
from apps.events.models import EventDates, Events
from scraping.logging_config import logger


def normalize(s):
    """Normalize a string for comparison (lowercase, alphanumeric only)."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def jaccard_similarity(a, b):
    """Compute Jaccard similarity between two strings (case-insensitive, word-based)."""
    set_a = set(re.findall(r"\w+", a.lower()))
    set_b = set(re.findall(r"\w+", b.lower()))
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def sequence_similarity(a, b):
    """Compute SequenceMatcher similarity between two strings (case-insensitive)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


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
        logger.warning(f"Failed to extract image URL from post: {e}")
        return None


def insert_event_to_db(event_data, ig_handle, source_url, club_type=None):
    """Map scraped event data to Event model fields, insert to DB"""
    shortcode = source_url.split("/")[-1] if source_url else "UNKNOWN"
    log_prefix = f"[{ig_handle}] [{shortcode}]"

    with transaction.atomic():
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
            logger.warning(f"{log_prefix} Event '{title}' missing occurrences; skipping insert")
            return "missing_occurrence"

        if not categories or not isinstance(categories, list):
            logger.warning(f"{log_prefix} Event '{title}' missing categories, assigning 'Uncategorized'")
            categories = ["Uncategorized"]

        if is_duplicate_event(event_data, ig_handle=ig_handle, source_url=source_url):
            return "duplicate"

        # Only fetch if club_type wasn't passed in
        if club_type is None:
            try:
                club = Clubs.objects.get(ig=ig_handle)
                club_type = club.club_type
            except Clubs.DoesNotExist:
                club_type = None
                logger.warning(f"{log_prefix} Club not found, setting club_type NULL")
        
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
                f"{log_prefix} Created {len(event_dates)} EventDates entries for event {event.id}"
            )
            return True
        except Exception as e:
            logger.error(f"{log_prefix} Error inserting event to DB: {e}")
            return False


def is_duplicate_event(event_data, ig_handle=None, source_url=None):
    """Check for duplicate events using title, occurrences, location, and description."""

    title = event_data.get("title") or ""
    location = event_data.get("location") or ""
    description = event_data.get("description") or ""
    occurrences = event_data.get("occurrences")

    log_prefix = f"[{ig_handle}] [{source_url.split('/')[-1] if source_url else 'UNKNOWN'}]"

    if not occurrences:
        return False

    target_start_str = occurrences[0].get("dtstart_utc")
    target_start = parse_utc_datetime(target_start_str)
    if not target_start:
        return False

    from datetime import timedelta
    day_start = target_start.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    try:
        candidates = EventDates.objects.select_related("event").filter(
            dtstart_utc__gte=day_start,
            dtstart_utc__lt=day_end
        )
        if candidates:
            logger.debug(f"{log_prefix} Found {len(candidates)} existing events on {day_start.date()} for duplicate check.")
            for i, cand in enumerate(candidates[:3]):
                evt = cand.event
                logger.debug(f"{log_prefix}   Candidate #{i+1}: '{evt.title}' @ {cand.dtstart_utc}")

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
                    f"{log_prefix} Duplicate by substring match: '{title}' @ '{location}' matches '{c_title}' @ '{c_loc}'"
                )
                return True

            if (title_sim > 0.7 and loc_sim > 0.5) or (
                loc_sim > 0.5 and desc_sim > 0.3
            ):
                logger.warning(
                    f"{log_prefix} Duplicate by similarity: '{title}' @ '{location}' matches '{c_title}' @ '{c_loc}' "
                    f"(title_sim={title_sim:.3f}, loc_sim={loc_sim:.3f}, desc_sim={desc_sim:.3f})"
                )
                return True
    except Exception as exc:
        logger.error(f"{log_prefix} Error during duplicate check: {exc!s}")

    return False


def append_event_to_csv(
    event_data,
    ig_handle,
    source_url,
    added_to_db="success",
    club_type=None,
):
    csv_file = Path(__file__).parent.parent / "scraping" / "events_scraped.csv"
    csv_file.parent.mkdir(parents=True, exist_ok=True)
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
        logger.info(f"[{ig_handle}] [{source_url.split('/')[-1] if source_url else 'UNKNOWN'}] Event written to CSV: '{title}' - Status: {added_to_db}")
