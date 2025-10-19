from datetime import timezone
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
        return handle_str if handle_str.startswith("@") else f"@{handle_str}"
    school = _get("school")
    return school or "Wat2Do Event"


def tz_compute(event_data, dtstart, dtend):
    """Compute dtstart_utc, dtend_utc, duration, all_day fields"""
    duration_val = None
    dtend_utc = None
    dtstart_utc = None
    all_day = False
    
    def _to_utc(dt):
        if not dt:
            return None
        if dt.tzinfo:
            return dt.astimezone(timezone.utc)
        return dt.replace(tzinfo=timezone.utc)
    
    try:
        if dtstart:
            dtstart_utc = _to_utc(dtstart)
        if dtstart and dtend:
            duration_val = dtend - dtstart
            dtend_utc = _to_utc(dtend)
    except Exception as e:
        logger.warning(f"Failed to compute duration/dtstart_utc/dtend_utc: {e!s}")

    return dtstart_utc, dtend_utc, duration_val, all_day
