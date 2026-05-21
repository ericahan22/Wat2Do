"""
Date utilities for semester end times and date-related operations.
"""

from datetime import datetime, time

import pytz
from bs4 import BeautifulSoup
from dateutil import parser as dateutil_parser
import requests

# Semester end times in format YYYYMMDDTHHMMSSZ (UTC)
# Index 0: Fall semester, Index 1: Winter semester, Index 2: Summer semester
UNIVERSITY_SEMESTER_END_TIMES = {
    "University of Waterloo": [
        "20251231T235959Z",  # Fall semester (ends December 31)
        "20260430T235959Z",  # Winter semester (ends April 30)
        "20260831T235959Z",  # Summer semester (ends August 31)
    ],
    "University of Pennsylvania": [
        "20251231T235959Z",  # Fall semester (ends December 31)
        "20260531T235959Z",  # Spring semester (ends May 31)
        "20260831T235959Z",  # Summer semester (ends August 31)
    ],
    "New York University": [
        "20251231T235959Z",  # Fall semester (ends December 31)
        "20260531T235959Z",  # Spring semester (ends May 31)
        "20260831T235959Z",  # Summer semester (ends August 31)
    ],
    "Columbia University": [
        "20251231T235959Z",  # Fall semester (ends December 31)
        "20260531T235959Z",  # Spring semester (ends May 31)
        "20260831T235959Z",  # Summer semester (ends August 31)
    ],
    "Massachusetts Institute of Technology": [
        "20251231T235959Z",  # Fall semester (ends December 31)
        "20260531T235959Z",  # Spring semester (ends May 31)
        "20260831T235959Z",  # Summer semester (ends August 31)
    ],
}

UNIVERSITY_DEFAULT_TIMEZONES = {
    "University of Waterloo": "America/Toronto",
    "University of Pennsylvania": "America/New_York",
    "New York University": "America/New_York",
    "Columbia University": "America/New_York",
    "Massachusetts Institute of Technology": "America/New_York",
}


def get_default_timezone(university: str = "University of Waterloo") -> str:
    """Return IANA timezone for a school. Falls back to America/Toronto."""
    return UNIVERSITY_DEFAULT_TIMEZONES.get(university, "America/Toronto")


_WATERLOO_TERM_END_CACHE: dict[str, str] = {}


def _get_waterloo_term_label(now: datetime) -> str:
    month = now.month
    year = now.year
    if 1 <= month <= 4:
        return f"Winter {year}"
    if 5 <= month <= 8:
        return f"Spring {year}"
    return f"Fall {year}"


def _parse_waterloo_classes_end_date(current_term: str) -> str | None:
    """Fetch the Waterloo undergraduate important-dates page and return the current term's classes end date."""
    try:
        url = "https://uwaterloo.ca/important-dates/undergraduate"
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("table tbody tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if not cells or len(cells) < 4:
                continue

            title = cells[0].get_text(" ", strip=True).lower()
            if "classes end" not in title:
                continue

            term_text = cells[2].get_text(" ", strip=True)
            if term_text != current_term:
                continue

            date_cell = cells[-1]
            date_text = ""
            date_span = date_cell.find("span", class_="important-dates--dates__start-date")
            if date_span:
                date_text = date_span.get_text(" ", strip=True)
            else:
                date_text = date_cell.get_text(" ", strip=True)

            if not date_text:
                continue

            parsed = dateutil_parser.parse(date_text)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=pytz.UTC)
                if parsed.time() == time(0, 0):
                    parsed = parsed.replace(hour=23, minute=59, second=59)
            else:
                parsed = parsed.astimezone(pytz.UTC)

            return parsed.strftime("%Y%m%dT%H%M%SZ")
    except Exception:
        return None


def get_waterloo_classes_end_time() -> str | None:
    """Return the real Waterloo classes end timestamp as a UTC string if available."""
    current_term = _get_waterloo_term_label(datetime.now())
    if current_term in _WATERLOO_TERM_END_CACHE:
        return _WATERLOO_TERM_END_CACHE[current_term]

    end_time = _parse_waterloo_classes_end_date(current_term)
    if end_time:
        _WATERLOO_TERM_END_CACHE[current_term] = end_time
    return end_time


def get_current_semester_end_time(university: str = "University of Waterloo") -> str:
    """
    Get the end time of the current semester based on the current date.

    Args:
        university: The university name (default: "University of Waterloo")

    Returns:
        A string in format YYYYMMDDTHHMMSSZ representing the end of the current semester

    Semester breakdown:
    - Fall: September 1 - December 31
    - Winter: January 1 - April 30
    - Summer: May 1 - August 31
    """

    if university == "University of Waterloo":
        waterloo_end_time = get_waterloo_classes_end_time()
        if waterloo_end_time:
            return waterloo_end_time

    semester_end_times = UNIVERSITY_SEMESTER_END_TIMES.get(
        university, UNIVERSITY_SEMESTER_END_TIMES["University of Waterloo"]
    )
    now = datetime.now()
    month = now.month

    # Determine current semester based on month
    if 1 <= month <= 4:
        # Winter semester (January - April)
        return semester_end_times[1]
    elif 5 <= month <= 8:
        # Summer semester (May - August)
        return semester_end_times[2]
    else:
        # Fall semester (September - December)
        return semester_end_times[0]


def parse_utc_datetime(dt_str: str):
    """
    Parse a datetime string to a timezone-aware UTC datetime object.

    Args:
        dt_str: A datetime string in any format that dateutil.parser can handle

    Returns:
        A timezone-aware datetime object in UTC

    Example:
        >>> parse_utc_datetime("2025-01-15T10:30:00Z")
        datetime.datetime(2025, 1, 15, 10, 30, 0, tzinfo=<UTC>)
    """
    if not dt_str:
        return None

    dt = dateutil_parser.parse(dt_str)
    dt = pytz.UTC.localize(dt) if dt.tzinfo is None else dt.astimezone(pytz.UTC)
    return dt
