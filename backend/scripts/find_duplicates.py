import os
import sys
from collections import defaultdict
import re
from difflib import SequenceMatcher
from datetime import timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from apps.events.models import Events, EventDates


def normalize(s):
    """Normalize a string for comparison (lowercase, alphanumeric only)."""
    if not s:
        return ""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def jaccard_similarity(a, b):
    """Compute Jaccard similarity between two strings (case-insensitive, word-based)."""
    if not a or not b:
        return 0.0
    set_a = set(re.findall(r"\w+", a.lower()))
    set_b = set(re.findall(r"\w+", b.lower()))
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def sequence_similarity(a, b):
    """Compute SequenceMatcher similarity between two strings (case-insensitive)."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def score_event(event):
    """Score an event based on data completeness. Higher score = better."""
    score = 0
    
    # Has description
    if event.description and len(event.description) > 10:
        score += 10
    
    # Has location
    if event.location:
        score += 5
    
    # Has coordinates
    if event.latitude and event.longitude:
        score += 3
    
    # Has food info
    if event.food:
        score += 2
    
    # Has price info
    if event.price is not None:
        score += 2
    
    # Has image
    if event.source_image_url:
        score += 3
    
    # Has club type
    if event.club_type:
        score += 2
    
    # Has categories
    if event.categories:
        score += 2
    
    # Has engagement stats
    if event.likes_count and event.likes_count > 0:
        score += 1
    if event.comments_count and event.comments_count > 0:
        score += 1
    
    # Prefer newer posts (they might have updated info)
    if event.posted_at:
        score += 1
    
    return score


def find_duplicates_by_source_url():
    """Find events with duplicate source URLs."""
    print("\n=== Finding duplicates by source_url ===")
    
    duplicates = (
        Events.objects.values('source_url')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
        .order_by('-count')
    )
    
    total_dupes = 0
    for dup in duplicates:
        events = Events.objects.filter(source_url=dup['source_url']).order_by('id')
        print(f"\nSource URL: {dup['source_url']}")
        print(f"Count: {dup['count']}")
        for event in events:
            print(f"  - ID: {event.id}, Title: {event.title}, Added: {event.added_at}")
import os
import sys
from collections import defaultdict
import re
from difflib import SequenceMatcher
from datetime import timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from apps.events.models import Events, EventDates


def normalize(s):
    """Normalize a string for comparison (lowercase, alphanumeric only)."""
    if not s:
        return ""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def jaccard_similarity(a, b):
    """Compute Jaccard similarity between two strings (case-insensitive, word-based)."""
    if not a or not b:
        return 0.0
    set_a = set(re.findall(r"\w+", a.lower()))
    set_b = set(re.findall(r"\w+", b.lower()))
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def sequence_similarity(a, b):
    """Compute SequenceMatcher similarity between two strings (case-insensitive)."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def score_event(event):
    """Score an event based on data completeness. Higher score = better."""
    score = 0
    
    # Has description
    if event.description and len(event.description) > 10:
        score += 10
    
    # Has location
    if event.location:
        score += 5
    
    # Has coordinates - REMOVED (fields don't exist)
    # if event.latitude and event.longitude:
    #     score += 3
    
    # Has food info
    if event.food:
        score += 2
    
    # Has price info
    if event.price is not None:
        score += 2
    
    # Has image
    if event.source_image_url:
        score += 3
    
    # Has club type
    if event.club_type:
        score += 2
    
    # Has categories
    if event.categories:
        score += 2
    
    # Has engagement stats
    if event.likes_count and event.likes_count > 0:
        score += 1
    if event.comments_count and event.comments_count > 0:
        score += 1
    
    # Prefer newer posts (they might have updated info)
    if event.posted_at:
        score += 1
    
    return score


def find_duplicates_by_source_url():
    """Find events with duplicate source URLs."""
    print("\n=== Finding duplicates by source_url ===")
    
    duplicates = (
        Events.objects.values('source_url')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
        .order_by('-count')
    )
    
    total_dupes = 0
    for dup in duplicates:
        events = Events.objects.filter(source_url=dup['source_url']).order_by('id')
        print(f"\nSource URL: {dup['source_url']}")
        print(f"Count: {dup['count']}")
        for event in events:
            print(f"  - ID: {event.id}, Title: {event.title}, Added: {event.added_at}")
        total_dupes += dup['count'] - 1
    
    print(f"\nTotal duplicate events to remove: {total_dupes}")
    return duplicates


def find_fuzzy_duplicates(days_lookback=365):
    """
    Find events that are likely duplicates using similarity logic.
    Checks events from (now - days_lookback) onwards.
    STRICTLY checks for events occurring on the SAME DAY.
    """
    print(f"\n=== Finding fuzzy duplicates (last {days_lookback} days) ===")
    
    # Similarity thresholds
    TITLE_SIMILARITY_THRESHOLD = 0.7
    LOCATION_SIMILARITY_THRESHOLD = 0.5
    DESCRIPTION_SIMILARITY_THRESHOLD = 0.3
    
    start_date = timezone.now() - timedelta(days=days_lookback)
    
    # Fetch relevant event dates
    dates_qs = EventDates.objects.filter(
        dtstart_utc__gte=start_date
    ).select_related('event').order_by('dtstart_utc')
    
    total_dates = dates_qs.count()
    print(f"Checking {total_dates} event dates...")
    
    duplicates = []
    checked_pairs = set()
    
    # Group by day for efficiency - STRICT SAME DAY CHECK
    events_by_day = defaultdict(list)
    for date_obj in dates_qs:
        if not date_obj.event:
            continue
        # Use local date if possible, but UTC date is fine for grouping 
        # as long as we compare within the bucket
        day_key = date_obj.dtstart_utc.date()
        events_by_day[day_key].append((date_obj, date_obj.event))
    
    print(f"Grouped into {len(events_by_day)} unique days")
    
    days_processed = 0
    for day, day_events in events_by_day.items():
        days_processed += 1
        if days_processed % 50 == 0:
            print(f"Processed {days_processed}/{len(events_by_day)} days...")
        
        if len(day_events) < 2:
            continue
        
        # Compare pairs within the same day
        for i in range(len(day_events)):
            date1, event1 = day_events[i]
            for j in range(i + 1, len(day_events)):
                date2, event2 = day_events[j]
                
                # Skip same event (different dates) or already checked
                if event1.id == event2.id:
                    continue
                
                pair_key = tuple(sorted([event1.id, event2.id]))
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)
                
                # Compare
                title1, title2 = event1.title or "", event2.title or ""
                loc1, loc2 = event1.location or "", event2.location or ""
                desc1, desc2 = event1.description or "", event2.description or ""
                
                norm_title1, norm_title2 = normalize(title1), normalize(title2)
                substring_match = norm_title1 in norm_title2 or norm_title2 in norm_title1
                
                title_sim = max(jaccard_similarity(title1, title2), sequence_similarity(title1, title2))
                loc_sim = jaccard_similarity(loc1, loc2)
                desc_sim = jaccard_similarity(desc1, desc2)
                
                is_duplicate = False
                reason = ""
                
                if substring_match and loc_sim > LOCATION_SIMILARITY_THRESHOLD:
                    is_duplicate = True
                    reason = f"substring + location (loc={loc_sim:.2f})"
                elif title_sim > TITLE_SIMILARITY_THRESHOLD and loc_sim > LOCATION_SIMILARITY_THRESHOLD:
                    is_duplicate = True
                    reason = f"title + location (title={title_sim:.2f}, loc={loc_sim:.2f})"
                elif loc_sim > LOCATION_SIMILARITY_THRESHOLD and desc_sim > DESCRIPTION_SIMILARITY_THRESHOLD:
                    is_duplicate = True
                    reason = f"location + desc (loc={loc_sim:.2f}, desc={desc_sim:.2f})"
                
                if is_duplicate:
                    duplicates.append({
                        'event1': event1,
                        'event2': event2,
                        'reason': reason,
                        'scores': (score_event(event1), score_event(event2))
                    })
    
    print(f"\nFound {len(duplicates)} fuzzy duplicate pairs")
    return duplicates


def delete_duplicate_source_urls(dry_run=True):
    """Delete exact duplicates by source_url."""
    print("\n=== Deleting duplicates by source_url ===")
    
    duplicates = (
        Events.objects.values('source_url')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )
    
    if duplicates.count() == 0:
        print("No duplicates found.")
        return
        
    to_delete_ids = []
    kept_ids = []
    
    for dup in duplicates:
        events = list(Events.objects.filter(source_url=dup['source_url']).order_by('id'))
        
        # Score and sort
        scored = [(score_event(e), e) for e in events]
        scored.sort(key=lambda x: (-x[0], x[1].id)) # High score first
        
        best = scored[0][1]
        kept_ids.append(best.id)
        
        for _, e in scored[1:]:
            to_delete_ids.append(e.id)
            if dry_run:
                print(f"[DRY RUN] Would delete ID {e.id} (duplicate of {best.id})")

    _perform_deletion(to_delete_ids, kept_ids, dry_run)


def delete_fuzzy_duplicates(dry_run=True):
    """Delete fuzzy duplicates found by similarity."""
    duplicates = find_fuzzy_duplicates()
    
    if not duplicates:
        return

    to_delete_ids = set()
    kept_ids = set()
    
    print("\n=== Resolving Fuzzy Duplicates ===")
    
    for dup in duplicates:
        e1 = dup['event1']
        e2 = dup['event2']
        
        # If one is already marked for deletion, skip
        if e1.id in to_delete_ids or e2.id in to_delete_ids:
            continue
            
        s1, s2 = dup['scores']
        
        # Pick winner
        if s1 >= s2:
            winner, loser = e1, e2
            w_score, l_score = s1, s2
        else:
            winner, loser = e2, e1
            w_score, l_score = s2, s1
            
        print(f"Match: '{e1.title}' vs '{e2.title}' ({dup['reason']})")
        print(f"  -> Keeping ID {winner.id} (score {w_score})")
        print(f"  -> Deleting ID {loser.id} (score {l_score})")
        
        to_delete_ids.add(loser.id)
        kept_ids.add(winner.id)

    _perform_deletion(list(to_delete_ids), list(kept_ids), dry_run)


def _perform_deletion(to_delete_ids, kept_ids, dry_run):
    """Helper to perform safe deletion."""
    count = len(to_delete_ids)
    if count == 0:
        return

    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  - To DELETE: {count}")
    print(f"  - To KEEP:   {len(kept_ids)}")
    print(f"{'='*60}")
    
    if dry_run:
        print("[DRY RUN] No changes made.")
        return

    response = input("\nType 'DELETE' to confirm deletion: ")
    if response != "DELETE":
        print("Cancelled.")
        return

    try:
        with transaction.atomic():
            print("Deleting...")
            Events.objects.filter(id__in=to_delete_ids).delete()
            print("Done.")
    except Exception as e:
        print(f"Error: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--find-source-dupes', action='store_true')
    parser.add_argument('--find-fuzzy-dupes', action='store_true')
    
    parser.add_argument('--delete-source-dupes', action='store_true')
    parser.add_argument('--delete-fuzzy-dupes', action='store_true')
    
    parser.add_argument('--no-dry-run', action='store_true')
    
    args = parser.parse_args()
    dry_run = not args.no_dry_run
    
    # If no args, just find everything
    if not any(vars(args).values()):
        find_duplicates_by_source_url()
        find_fuzzy_duplicates()
        return

    if args.find_source_dupes:
        find_duplicates_by_source_url()
    if args.find_fuzzy_dupes:
        find_fuzzy_duplicates()
        
    if args.delete_source_dupes:
        delete_duplicate_source_urls(dry_run)
    if args.delete_fuzzy_dupes:
        delete_fuzzy_duplicates(dry_run)

if __name__ == "__main__":
    main()
