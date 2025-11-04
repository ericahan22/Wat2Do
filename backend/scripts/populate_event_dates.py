"""
Script to populate the EventDates table from existing Events.

This script:
1. Creates EventDates entries for all events without rrule/rdate (single occurrence)
2. Parses rrule fields and creates multiple EventDates entries for recurring events
3. Parses rdate fields and creates EventDates entries for specific dates

Run with: python scripts/populate_event_dates.py
"""

import os
import sys
from datetime import datetime, timedelta
from dateutil import rrule as rrule_lib
from dateutil import parser as dateutil_parser
import pytz

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.utils import timezone
from django.db import transaction
from apps.events.models import Events, EventDates
from utils.event_dates_utils import (
    parse_rdate_string,
    parse_rrule_string,
    calculate_end_time,
)


def create_event_dates_for_event(event, dry_run=False):
    """
    Create EventDates entries for a single event.
    Returns the number of entries that would be/were created.
    """
    entries_created = 0
    
    # Check if event already has EventDates entries
    existing_count = EventDates.objects.filter(event=event).count()
    if existing_count > 0:
        print(f"  Skipping event {event.id}: already has {existing_count} EventDates entries")
        return 0
    
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
        print(f"  Processing rrule: {event.rrule}")
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
                except Exception as e:
                    print(f"  Warning: Could not parse rdate from list '{date_str}': {e}")
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
    
    # Create EventDates entries for each occurrence
    if not dry_run:
        event_dates_to_create = []
        
        for occurrence in occurrences:
            # Calculate end time for this occurrence
            occurrence_utc = occurrence.astimezone(pytz.UTC)
            occurrence_end = calculate_end_time(dtstart, dtend, duration, occurrence)
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
            event_dates_to_create.append(event_date)
            entries_created += 1
        
        # Bulk create for efficiency
        if event_dates_to_create:
            EventDates.objects.bulk_create(event_dates_to_create)
    else:
        entries_created = len(occurrences)
    
    return entries_created


def populate_event_dates(dry_run=False, limit=None):
    """
    Main function to populate EventDates table from all Events.
    
    Args:
        dry_run: If True, only print what would be done without making changes
        limit: If set, only process this many events (for testing)
    """
    print("=" * 80)
    print("EVENT DATES POPULATION SCRIPT")
    print("=" * 80)
    
    if dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")
    
    # Get all events
    events = Events.objects.all().order_by('id')
    
    if limit:
        events = events[:limit]
        print(f"Processing {limit} events (limited for testing)\n")
    else:
        print(f"Processing {events.count()} total events\n")
    
    total_entries = 0
    events_with_rrule = 0
    events_with_rdate = 0
    events_simple = 0
    errors = 0
    
    for event in events:
        try:
            print(f"Event {event.id}: {event.title[:50] if event.title else 'untitled'}")
            
            entries = create_event_dates_for_event(event, dry_run=dry_run)
            total_entries += entries
            
            if event.rrule:
                events_with_rrule += 1
            elif event.rdate:
                events_with_rdate += 1
            else:
                events_simple += 1
            
            print(f"  Created {entries} EventDates entries")
            
        except Exception as e:
            print(f"  ERROR processing event {event.id}: {e}")
            errors += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total events processed: {events.count()}")
    print(f"  - Simple events (no recurrence): {events_simple}")
    print(f"  - Events with rrule: {events_with_rrule}")
    print(f"  - Events with rdate: {events_with_rdate}")
    print(f"Total EventDates entries created: {total_entries}")
    print(f"Errors: {errors}")
    
    if dry_run:
        print("\n*** This was a DRY RUN - no changes were made ***")
    else:
        print("\n✓ EventDates table successfully populated!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate EventDates table from Events')
    parser.add_argument('--dry-run', action='store_true', help='Run without making changes')
    parser.add_argument('--limit', type=int, help='Limit number of events to process')
    
    args = parser.parse_args()
    
    populate_event_dates(dry_run=args.dry_run, limit=args.limit)



