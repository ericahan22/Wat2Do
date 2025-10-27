from datetime import timezone
from zoneinfo import ZoneInfo

from dateutil import parser as dateutil_parser

from scraping.logging_config import logger


def determine_display_handle(event):
    """
    Determine a display handle for an event.
    Accepts either a dict-like object (with .get) or a Django model instance (attributes).
    Prefers social handles in order: ig, discord, x, tiktok, fb. Prepends '@' unless already present.
    Falls back to event.school or "Wat2Do Event".
    """

    def _get(key):
        # dict
        if hasattr(event, "get"):
            return event.get(key)
        # model instance / object
        return getattr(event, key, None)

    social_handles = [
        _get("ig_handle"),
        _get("discord_handle"),
        _get("x_handle"),
        _get("tiktok_handle"),
        _get("fb_handle"),
    ]
    social_handles = [h for h in social_handles if h]

    if social_handles:
        handle = social_handles[0]
        handle_str = str(handle)
        return handle_str
    school = _get("school")
    return school or "Wat2Do Event"


def tz_compute(dtstart, dtend, local_tz="America/Toronto"):
    """Compute UTC-aware dtstart_utc, dtend_utc, duration, all_day fields, assuming local time if naive."""
    duration = None
    dtend_utc = None
    dtstart_utc = None
    all_day = False

    def _to_utc(dt):
        if not dt:
            return None
        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc)
        # Assume naive datetimes are in local time (America/Toronto)
        try:
            local_zone = ZoneInfo(local_tz)
            dt_local = dt.replace(tzinfo=local_zone)
            return dt_local.astimezone(timezone.utc)
        except Exception as e:
            logger.warning(f"Failed to localize naive datetime {dt!r}: {e!s}")
            return dt.replace(tzinfo=timezone.utc)

    def _ensure_dt(obj):
        """Accept datetime or ISO string, return datetime or None."""
        if not obj:
            return None
        if isinstance(obj, str):
            try:
                return dateutil_parser.parse(obj)
            except Exception as e:
                logger.warning(f"Failed to parse datetime string {obj!r}: {e!s}")
                return None
        return obj

    try:
        dtstart_dt = _ensure_dt(dtstart)
        dtend_dt = _ensure_dt(dtend)

        if dtstart_dt:
            dtstart_utc = _to_utc(dtstart_dt)
        if dtstart_dt and dtend_dt:
            duration = dtend_dt - dtstart_dt
            dtend_utc = _to_utc(dtend_dt)
    except Exception as e:
        logger.warning(f"Failed to compute duration/dtstart_utc/dtend_utc: {e!s}")

    return dtstart_utc, dtend_utc, duration, all_day
