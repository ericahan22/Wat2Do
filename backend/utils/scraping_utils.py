import csv
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from django.db import transaction
from django.utils import timezone

from apps.clubs.models import Clubs
from apps.events.models import EventDates, Events
from scraping.logging_config import logger
from utils.date_utils import parse_utc_datetime


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


def insert_event_to_db(
    event_data,
    ig_handle,
    source_url,
    club_type=None,
    big_scrape=False,
    dry_run=False,
):
    """Map scraped event data to Event model fields, insert to DB"""
    shortcode = source_url.strip("/").split("/")[-1] if source_url else "UNKNOWN"
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

        # New data fields
        comments_count = event_data.get("comments_count", 0)
        likes_count = event_data.get("likes_count", 0)
        posted_at = event_data.get("posted_at")

        if not occurrences:
            logger.warning(
                f"{log_prefix} Event '{title}' missing occurrences; skipping insert"
            )
            return "missing_occurrence"

        if not categories or not isinstance(categories, list):
            logger.warning(
                f"{log_prefix} Event '{title}' missing categories, assigning 'Uncategorized'"
            )
            categories = ["Uncategorized"]

        # Check for duplicate by source_url ONLY
        if big_scrape:
            try:
                existing_event = Events.objects.get(source_url=source_url)
                if dry_run:
                    logger.info(
                        f"{log_prefix} [DRY RUN] Found existing event '{existing_event.title}' by source_url. Updating data (food, comments, likes, posted_at)."
                    )
                    return "updated_data"

                logger.info(
                    f"{log_prefix} Found existing event '{existing_event.title}' by source_url. Updating data (food, comments, likes, posted_at)."
                )
                existing_event.food = food[:255] if food else None
                existing_event.comments_count = comments_count
                existing_event.likes_count = likes_count
                if posted_at:
                    existing_event.posted_at = posted_at
                existing_event.save()
                return "updated_data"
            except Events.DoesNotExist:
                # If not found, proceed to DB insertion
                pass

        # Normal Mode: Use fuzzy duplicate detection
        if not big_scrape:
            detector = EventDuplicateDetector()
            has_match, matched_event = detector.find_match(
                event_data, ig_handle=ig_handle, source_url=source_url
            )

            if has_match:
                # If event is from same club, update event info
                if matched_event and matched_event.ig_handle == ig_handle:
                    if dry_run:
                        logger.info(
                            f"{log_prefix} [DRY RUN] Updating existing event '{matched_event.title}' (ID: {matched_event.id}) with new date/time/location"
                        )
                        return "updated"

                    logger.info(
                        f"{log_prefix} Updating existing event '{matched_event.title}' (ID: {matched_event.id}) with new date/time/location"
                    )

                    # Only update location, date, and time
                    matched_event.location = location
                    matched_event.source_url = source_url
                    matched_event.added_at = timezone.now()  # Bump to top
                    matched_event.save()

                    # Delete old event dates and create new ones
                    EventDates.objects.filter(event=matched_event).delete()
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
                                event=matched_event,
                                dtstart_utc=dtstart_utc,
                                dtend_utc=dtend_utc,
                                duration=occ.get("duration") or None,
                                tz=occ.get("tz") or None,
                            )
                        )
                    EventDates.objects.bulk_create(event_dates)
                    logger.info(
                        f"{log_prefix} Updated event with {len(event_dates)} new date(s)"
                    )
                    return "updated"
                else:
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
            "club_type": club_type[:50] if club_type else None,
            "location": location,
            "food": food[:255] if food else None,
            "price": price,
            "registration": registration,
            "description": description or None,
            "reactions": {},
            "source_image_url": source_image_url or None,
            "status": "CONFIRMED",
            "school": school[:255] if school else "",
            "categories": categories,
            "comments_count": comments_count,
            "likes_count": likes_count,
            "posted_at": posted_at,
        }

        if dry_run:
            logger.info(
                f"{log_prefix} [DRY RUN] Creating new event '{title}'"
            )
            return True

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


class EventDuplicateDetector:
    """Handles duplicate event detection"""

    def __init__(self):
        self.SAME_CLUB_TITLE_THRESHOLD = 0.8
        self.TITLE_SIMILARITY_THRESHOLD = 0.7
        self.LOCATION_SIMILARITY_THRESHOLD = 0.5
        self.DESCRIPTION_SIMILARITY_THRESHOLD = 0.3

    def find_match(self, event_data, ig_handle=None, source_url=None):
        """
        Check for duplicate events using title, occurrences, location, and description.
        Returns:
            tuple: (has_match: bool, matched_event: Event | None)
            - has_match: True if a matching event was found (could be duplicate or update)
            - matched_event: The matching event object if found, None otherwise
        """
        title = event_data.get("title") or ""
        location = event_data.get("location") or ""
        description = event_data.get("description") or ""
        occurrences = event_data.get("occurrences")

        shortcode = source_url.strip("/").split("/")[-1] if source_url else "UNKNOWN"
        log_prefix = f"[{ig_handle}] [{shortcode}]"

        if not occurrences:
            return False, None

        target_start_str = occurrences[0].get("dtstart_utc")
        target_start = parse_utc_datetime(target_start_str)
        if not target_start:
            return False, None

        try:
            # Strategy 1: Check for same-club updates (regardless of date)
            matched_event = self._check_same_club_update(ig_handle, title, log_prefix)
            if matched_event:
                return True, matched_event

            # Strategy 2: Check for same-day duplicates
            matched_event = self._check_same_day_duplicate(
                target_start, title, location, description, ig_handle, log_prefix
            )
            if matched_event:
                return True, matched_event

        except Exception as exc:
            logger.error(f"{log_prefix} Error during duplicate check: {exc!s}")

        return False, None

    def _check_same_club_update(self, ig_handle, title, log_prefix):
        """
        Check if the same club has posted a similar event before (regardless of date).
        This catches updates where the club reposts with a new date/location.
        Returns:
            Event | None: The matched event if found, None otherwise
        """
        if not ig_handle:
            return None

        same_club_events = Events.objects.filter(ig_handle=ig_handle).prefetch_related(
            "event_dates"
        )
        now = timezone.now()

        for existing_event in same_club_events:
            # Check if event is in the past
            dates = list(existing_event.event_dates.all())
            if not dates:
                continue

            # Get the latest end time (or start time)
            latest_end = max((d.dtend_utc or d.dtstart_utc) for d in dates)

            # If the event has already passed, treat as new event
            if latest_end < now:
                continue

            c_title = getattr(existing_event, "title", "") or ""

            title_sim = max(
                jaccard_similarity(c_title, title),
                sequence_similarity(c_title, title),
            )

            if title_sim > self.SAME_CLUB_TITLE_THRESHOLD:
                logger.warning(
                    f"{log_prefix} Potential update detected: '{title}' matches existing event '{c_title}' "
                    f"from same club (title_sim={title_sim:.3f}). This will be updated."
                )
                return existing_event

        return None

    def _check_same_day_duplicate(
        self, target_start, title, location, description, ig_handle, log_prefix
    ):
        """
        Check for duplicate events on the same day using title, location, and description similarity.
        Returns:
            Event | None: The matched event if found, None otherwise
        """
        from datetime import timedelta

        day_start = target_start.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        candidates = EventDates.objects.select_related("event").filter(
            dtstart_utc__gte=day_start, dtstart_utc__lt=day_end
        )

        if candidates:
            logger.debug(
                f"{log_prefix} Found {len(candidates)} existing events on {day_start.date()} for duplicate check."
            )
            for i, cand in enumerate(candidates[:3]):
                evt = cand.event
                logger.debug(
                    f"{log_prefix}   Candidate #{i+1}: '{evt.title}' @ {cand.dtstart_utc}"
                )

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

            # Check substring match
            norm_title = normalize(title)
            norm_c_title = normalize(c_title)
            substring_match = norm_c_title in norm_title or norm_title in norm_c_title

            # Calculate similarities
            title_sim = max(
                jaccard_similarity(c_title, title),
                sequence_similarity(c_title, title),
            )
            loc_sim = jaccard_similarity(c_loc, location)
            desc_sim = jaccard_similarity(c_desc, description)

            # Check if substring match + similar location
            if substring_match:
                similar_location = loc_sim > self.LOCATION_SIMILARITY_THRESHOLD
                if similar_location:
                    logger.warning(
                        f"{log_prefix} Duplicate by substring match + location: '{title}' @ '{location}' matches '{c_title}' @ '{c_loc}' "
                        f"(ig_handle: {ig_handle} vs {existing_event.ig_handle}, loc_sim={loc_sim:.3f})"
                    )
                    return existing_event
                else:
                    logger.debug(
                        f"{log_prefix} Substring match but different location: '{title}' ({ig_handle}) @ '{location}' vs '{c_title}' ({existing_event.ig_handle}) @ '{c_loc}' (loc_sim={loc_sim:.3f})"
                    )
                    continue

            # Check similarity thresholds
            if (
                title_sim > self.TITLE_SIMILARITY_THRESHOLD
                and loc_sim > self.LOCATION_SIMILARITY_THRESHOLD
            ) or (
                loc_sim > self.LOCATION_SIMILARITY_THRESHOLD
                and desc_sim > self.DESCRIPTION_SIMILARITY_THRESHOLD
            ):
                logger.warning(
                    f"{log_prefix} Duplicate by similarity: '{title}' @ '{location}' matches '{c_title}' @ '{c_loc}' "
                    f"(title_sim={title_sim:.3f}, loc_sim={loc_sim:.3f}, desc_sim={desc_sim:.3f})"
                )
                return existing_event

        return None


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
        shortcode = source_url.strip("/").split("/")[-1] if source_url else "UNKNOWN"
        logger.info(
            f"[{ig_handle}] [{shortcode}] Event written to CSV - Status: {added_to_db}"
        )
