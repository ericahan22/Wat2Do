"""
Utility functions for creating and managing EventDates entries.
"""

from datetime import datetime, timedelta
from dateutil import rrule as rrule_lib
from dateutil import parser as dateutil_parser
import pytz
from django.utils import timezone


def parse_rdate_string(rdate_str):
    """
    Parse rdate string which is comma-separated datetime strings.
    Format: "20251113T170000,20251204T170000,20251218T170000"
    Returns list of datetime objects.
    """
    if not rdate_str or not isinstance(rdate_str, str):
        return []
    
    dates = []
    for date_part in rdate_str.split(','):
        date_part = date_part.strip()
        if not date_part:
            continue
        try:
            # Parse iCalendar format: YYYYMMDDTHHMMSS
            if 'T' in date_part and len(date_part) == 15:
                dt = datetime.strptime(date_part, '%Y%m%dT%H%M%S')
            else:
                # Try general parsing
                dt = dateutil_parser.parse(date_part)
            dates.append(dt)
        except Exception:
            # Silently skip unparseable dates
            pass
    
    return dates


def parse_rrule_string(rrule_str, dtstart, tz_str=None):
    """
    Parse rrule string and generate occurrences.
    Returns list of datetime objects.
    Limits to 100 occurrences to prevent infinite loops.
    """
    if not rrule_str:
        return []
    
    try:
        # Get timezone
        tz = pytz.timezone(tz_str) if tz_str else pytz.UTC
        
        # Ensure dtstart is timezone-aware
        if timezone.is_naive(dtstart):
            dtstart = timezone.make_aware(dtstart, tz)
        
        # Parse the rrule string
        rule = rrule_lib.rrulestr(rrule_str, dtstart=dtstart)
        
        # Generate occurrences (limit to 100 to be safe)
        occurrences = []
        count = 0
        max_occurrences = 100
        
        for dt in rule:
            occurrences.append(dt)
            count += 1
            if count >= max_occurrences:
                break
        
        return occurrences
    except Exception:
        return []


def calculate_end_time(dtstart, dtend, duration, occurrence_date):
    """
    Calculate the end time for an occurrence.
    If dtend exists, calculate the offset from dtstart and apply it.
    Otherwise use duration if available.
    """
    if dtend:
        # Calculate the duration between dtstart and dtend
        time_diff = dtend - dtstart
        return occurrence_date + time_diff
    elif duration:
        return occurrence_date + duration
    else:
        return None


def create_event_dates_from_event_data(event, event_data=None):
    """
    Create EventDates entries for a single event.
    
    Args:
        event: The Events model instance
        event_data: Optional dict with event data (for compatibility)
    
    Returns:
        list of EventDates objects (not yet saved to DB)
    """
    from apps.events.models import EventDates
    
    # Get timezone
    tz_str = event.tz or 'UTC'
    try:
        tz = pytz.timezone(tz_str)
    except:
        tz = pytz.UTC
    
    # Ensure datetimes are timezone-aware
    dtstart = event.dtstart
    dtend = event.dtend
    dtstart_utc = event.dtstart_utc
    dtend_utc = event.dtend_utc
    duration = event.duration
    
    if timezone.is_naive(dtstart):
        dtstart = timezone.make_aware(dtstart, tz)
    if dtend and timezone.is_naive(dtend):
        dtend = timezone.make_aware(dtend, tz)
    if timezone.is_naive(dtstart_utc):
        dtstart_utc = timezone.make_aware(dtstart_utc, pytz.UTC)
    if dtend_utc and timezone.is_naive(dtend_utc):
        dtend_utc = timezone.make_aware(dtend_utc, pytz.UTC)
    
    occurrences = []
    
    # Case 1: Event has rrule (recurring pattern)
    if event.rrule:
        rrule_dates = parse_rrule_string(event.rrule, dtstart, tz_str)
        occurrences.extend(rrule_dates)
    
    # Case 2: Event has rdate (specific additional dates)
    elif event.rdate:
        # rdate might be stored as JSON array or as string
        if isinstance(event.rdate, list):
            # JSON array format
            for date_str in event.rdate:
                try:
                    dt = dateutil_parser.parse(str(date_str))
                    if timezone.is_naive(dt):
                        dt = timezone.make_aware(dt, tz)
                    occurrences.append(dt)
                except Exception:
                    pass
        elif isinstance(event.rdate, str):
            # String format (comma-separated)
            rdate_dates = parse_rdate_string(event.rdate)
            for dt in rdate_dates:
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt, tz)
                occurrences.append(dt)
        
        # For rdate, also include the primary dtstart
        occurrences.append(dtstart)
    
    # Case 3: Simple event (no recurrence)
    else:
        occurrences.append(dtstart)
    
    # Create EventDates objects for each occurrence
    event_dates_list = []
    
    for occurrence in occurrences:
        occurrence_end = calculate_end_time(dtstart, dtend, duration, occurrence)
        
        if not event.rrule and not event.rdate:
            occurrence_utc = dtstart_utc
            occurrence_end_utc = dtend_utc
        else:
            occurrence_utc = occurrence.astimezone(pytz.UTC)
            occurrence_end_utc = occurrence_end.astimezone(pytz.UTC) if occurrence_end else None
        
        event_date = EventDates(
            event=event,
            dtstart=occurrence,
            dtend=occurrence_end,
            dtstart_utc=occurrence_utc,
            dtend_utc=occurrence_end_utc,
            duration=duration,
            tz=tz_str,
        )
        event_dates_list.append(event_date)
    
    return event_dates_list



