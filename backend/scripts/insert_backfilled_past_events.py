"""
Insert backfilled past-date events from a CSV into the DB.

Reads a `events_scraped.csv` produced by the big scrape, picks rows where
`added_to_db == "event_past_date"` AND `ig_handle` is populated (backfilled),
and runs them through the standard insert_event_to_db() pipeline so we get
the same dedup logic the scraper uses.

Usage:
    python scripts/insert_backfilled_past_events.py --csv PATH [--dry-run]

In --dry-run mode every insert is rolled back, so nothing commits to the DB
but you get accurate counts for what *would* happen.
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.db import transaction
from django.db.transaction import set_rollback

from utils.scraping_utils import insert_event_to_db

csv.field_size_limit(sys.maxsize)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, type=Path)
    p.add_argument("--dry-run", action="store_true",
                   help="Roll back every insert. Counts are still accurate.")
    p.add_argument("--limit", type=int, default=0,
                   help="Process only the first N candidate rows (0 = all).")
    return p.parse_args()


def parse_posted_at(s: str):
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s.replace("Z", "+0000") if fmt.endswith("Z") else s, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def row_to_event_data(row: dict) -> dict:
    def jload(s, default):
        if not s:
            return default
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return default

    def maybe_float(s):
        if s is None or s == "":
            return None
        try:
            return float(s)
        except ValueError:
            return None

    def maybe_int(s, default=0):
        if s is None or s == "":
            return default
        try:
            return int(s)
        except ValueError:
            return default

    return {
        "ig_handle": row.get("ig_handle") or None,
        "title": row.get("title") or "",
        "source_url": row.get("source_url") or None,
        "location": row.get("location") or None,
        "food": row.get("food") or None,
        "price": row.get("price") or None,
        "registration": row.get("registration", "").lower() == "true",
        "description": row.get("description") or "",
        "latitude": maybe_float(row.get("latitude")),
        "longitude": maybe_float(row.get("longitude")),
        "school": row.get("school") or "",
        "source_image_url": row.get("source_image_url") or "",
        "club_type": row.get("club_type") or None,
        "categories": jload(row.get("categories"), []),
        "occurrences": jload(row.get("occurrences"), []),
        "likes_count": maybe_int(row.get("likes_count"), 0),
        "comments_count": maybe_int(row.get("comments_count"), 0),
        "posted_at": parse_posted_at(row.get("posted_at") or ""),
    }


def main():
    args = parse_args()

    if not args.csv.is_file():
        print(f"CSV not found: {args.csv}", file=sys.stderr)
        sys.exit(1)

    candidates = []
    with args.csv.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("added_to_db") == "event_past_date" and row.get("ig_handle"):
                candidates.append(row)

    if args.limit:
        candidates = candidates[: args.limit]

    print(f"Candidate rows to process: {len(candidates)}")
    print(f"Mode: {'DRY-RUN (rollback)' if args.dry_run else 'COMMIT'}")
    print(f"Target DB host: {os.getenv('POSTGRES_HOST') or '(from DATABASE_URL)'}")
    print()

    outcomes = Counter()
    sample_per_outcome = {}

    for i, row in enumerate(candidates, start=1):
        event_data = row_to_event_data(row)
        try:
            with transaction.atomic():
                result = insert_event_to_db(event_data)
                if args.dry_run:
                    set_rollback(True)
        except Exception as e:
            result = f"exception: {type(e).__name__}"
            outcomes[result] += 1
            sample_per_outcome.setdefault(
                result,
                {"title": event_data.get("title"), "ig_handle": event_data.get("ig_handle"), "err": str(e)[:200]},
            )
            continue

        # Normalize result label
        if result is True:
            label = "would_insert" if args.dry_run else "inserted"
        elif result is False:
            label = "error"
        else:
            label = str(result)

        outcomes[label] += 1
        if label not in sample_per_outcome:
            sample_per_outcome[label] = {
                "title": event_data.get("title"),
                "ig_handle": event_data.get("ig_handle"),
                "source_url": event_data.get("source_url"),
            }

        if i % 200 == 0:
            print(f"  ...processed {i}/{len(candidates)}: {dict(outcomes)}")

    print()
    print("=== SUMMARY ===")
    for k, v in outcomes.most_common():
        print(f"  {k:<22} {v}")
    print()
    print("=== SAMPLE PER OUTCOME ===")
    for k, sample in sample_per_outcome.items():
        print(f"  {k}: {sample}")


if __name__ == "__main__":
    main()
