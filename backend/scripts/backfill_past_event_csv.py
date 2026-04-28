"""
Flatten multi-line CSV cells and backfill missing context fields on
event_past_date rows by matching their AI-extracted description/title against
the original Apify post captions.

Inputs:
  --csv      Path to events_scraped.csv (raw, from big_scrape artifact)
  --apify    Path to apify_raw_results.json (same artifact)
  --out      Output path for the corrected CSV

Backfilled fields (only on rows where added_to_db == "event_past_date" and
ig_handle is empty): ig_handle, source_url, posted_at, likes_count, comments_count.

The flatten step also collapses whitespace runs in the description and
location fields so each row is exactly one line of CSV.
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)


QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-"})


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, type=Path)
    p.add_argument("--apify", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    return p.parse_args()


def norm(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s.lower().translate(QUOTE_MAP)).strip()


def flatten(s: str) -> str:
    if not s:
        return s
    return re.sub(r"\s+", " ", str(s)).strip()


def fmt_ts(iso: str) -> str:
    if not iso:
        return ""
    s = iso.replace("T", " ").rstrip("Z")
    s = re.sub(r"\.\d+$", "", s)
    return s + "+00:00"


def build_post_index(apify_path: Path):
    with apify_path.open() as f:
        posts = json.load(f)
    seen = {}
    for p in posts:
        cap = p.get("caption") or ""
        url = p.get("url") or ""
        handle = p.get("ownerUsername") or ""
        if cap and url and handle and url not in seen:
            seen[url] = {
                "caption_n": norm(cap),
                "url": url,
                "handle": handle,
                "timestamp": p.get("timestamp") or "",
                "likes": p.get("likesCount") or p.get("likeCount") or 0,
                "comments": p.get("commentsCount") or p.get("commentCount") or 0,
            }
    return list(seen.values())


def make_finder(posts_idx):
    def find_post(desc, title):
        desc_n = norm(desc)
        title_n = norm(title)
        for L in (200, 120, 80, 50, 30, 20):
            if len(desc_n) >= L:
                needle = desc_n[:L]
                ms = [p for p in posts_idx if needle in p["caption_n"]]
                if len(ms) == 1:
                    return ms[0]
        if title_n and len(title_n) >= 8:
            ms = [p for p in posts_idx if title_n in p["caption_n"]]
            if len(ms) == 1:
                return ms[0]
        return None
    return find_post


FLATTEN_FIELDS = {"description", "location"}


def main():
    args = parse_args()

    posts_idx = build_post_index(args.apify)
    print(f"Indexed {len(posts_idx)} unique apify posts")

    finder = make_finder(posts_idx)
    backfilled = unmatched = passthrough = 0

    with args.csv.open("r", encoding="utf-8", newline="") as fin, \
         args.out.open("w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin)
        fields = reader.fieldnames
        writer = csv.DictWriter(fout, fieldnames=fields, lineterminator="\n")
        writer.writeheader()

        for row in reader:
            for k in FLATTEN_FIELDS:
                if k in row and row[k]:
                    row[k] = flatten(row[k])

            if row.get("added_to_db") == "event_past_date" and not row.get("ig_handle"):
                m = finder(row.get("description"), row.get("title"))
                if m:
                    row["ig_handle"] = m["handle"]
                    row["source_url"] = m["url"]
                    row["posted_at"] = fmt_ts(m["timestamp"])
                    row["likes_count"] = m["likes"]
                    row["comments_count"] = m["comments"]
                    backfilled += 1
                else:
                    unmatched += 1
            else:
                passthrough += 1

            writer.writerow(row)

    print(f"Backfilled past_date rows: {backfilled}")
    print(f"Unmatched past_date rows : {unmatched}")
    print(f"Passthrough rows         : {passthrough}")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
