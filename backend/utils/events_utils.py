from dateutil import parser as dateutil_parser
from datetime import timedelta
import re


def clean_datetime(val):
    if not val or not isinstance(val, str) or not val.strip():
        return None
    try:
        return dateutil_parser.parse(val)
    except Exception:
        return None


def clean_duration(val):
    if not val or str(val).strip() == "":
        return None
    if isinstance(val, timedelta):
        return val
    if isinstance(val, str):
        match = re.match(r"^(\d{1,2}):(\d{2}):(\d{2})$", val)
        if match:
            hours, minutes, seconds = map(int, match.groups())
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    return None


def determine_display_handle(event):
    """
    Determine a display handle for an event.
    Accepts either a dict-like object (with .get) or a Django model instance (attributes).
    Prefers ig_handle, then other_handle, then event.school.
    """

    def _get(key):
        # dict
        if hasattr(event, "get"):
            return event.get(key)
        # model instance / object
        return getattr(event, key, None)

    ig_handle = _get("ig_handle")
    other_handle = _get("other_handle")
    school = _get("school")

    if ig_handle:
        return str(ig_handle)
    if other_handle:
        return str(other_handle)
    return school or "Wat2Do Event"
