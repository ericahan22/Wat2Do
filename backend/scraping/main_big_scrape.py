"""
Big Scrape entry point.

Scrapes Instagram accounts listed in a URLs file and inserts events into the
configured database, stamped with the given school.

Usage:
    python main_big_scrape.py \\
        --urls-file PATH \\
        --school NAME \\
        --limit N \\
        --cutoff-days N \\
        [--dry-run]
"""

import argparse
import asyncio
import json
import os
import sys
import urllib.request
from datetime import timedelta
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.utils import timezone

from apps.scraping.models import ScrapeRun
from scraping.event_processor import EventProcessor
from scraping.instagram_scraper import InstagramScraper
from scraping.logging_config import logger


# How many handles to send to Apify in one actor run. Each chunk gets its own
# 1-hour timeout. Larger chunks = fewer actor starts but more risk of timing
# out; smaller chunks = more actor starts but each finishes faster.
HANDLES_PER_APIFY_RUN = 100


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Big Scrape entry point")
    parser.add_argument(
        "--urls-file",
        type=Path,
        help=(
            "Path to a text file with one Instagram URL per line. "
            "Blank lines and lines starting with '#' are ignored. "
            "Required unless --apify-dataset-ids is given."
        ),
    )
    parser.add_argument(
        "--apify-dataset-ids",
        default="",
        help=(
            "Comma-separated Apify dataset IDs to load posts from instead of "
            "running the actor. Skips Apify scraping; --urls-file is ignored."
        ),
    )
    parser.add_argument(
        "--school",
        required=True,
        help='School name (e.g. "University of Waterloo").',
    )
    parser.add_argument(
        "--limit",
        type=int,
        required=True,
        help="Max posts per user to fetch.",
    )
    parser.add_argument(
        "--cutoff-days",
        type=int,
        required=True,
        help="Number of days to look back for posts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process only the first URL in the file.",
    )
    parser.add_argument(
        "--model",
        default="gpt-5-mini",
        help="OpenAI model used for event extraction.",
    )
    return parser.parse_args()


def read_urls_file(path: Path) -> list[str]:
    """Read URLs from a text file. One per line; blanks and '#' comments ignored."""
    if not path.is_file():
        raise FileNotFoundError(f"URLs file not found: {path}")
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def urls_to_handles(urls: list[str]) -> list[str]:
    return [
        url.split("instagram.com/")[1].split("/")[0]
        for url in urls
        if "instagram.com/" in url
    ]


def filter_valid_posts(posts):
    return [
        post
        for post in posts
        if not post.get("error")
        and not post.get("errorDescription")
        and post.get("url")
        and "/p/" in post.get("url")
    ]


def fetch_apify_dataset(dataset_id: str) -> list[dict]:
    """Download all items from an Apify dataset by ID."""
    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json&clean=true"
    logger.info(f"Fetching Apify dataset {dataset_id}...")
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.load(r)


def main() -> None:
    args = parse_args()
    dataset_ids = [s.strip() for s in (args.apify_dataset_ids or "").split(",") if s.strip()]
    use_datasets = bool(dataset_ids)

    logger.info(
        f"--- Big Scrape Started: school={args.school!r}, "
        f"{'dataset_ids=' + str(dataset_ids) if use_datasets else 'urls_file=' + str(args.urls_file)}, "
        f"dry_run={args.dry_run}, limit={args.limit}, cutoff_days={args.cutoff_days}, "
        f"model={args.model!r} ---"
    )

    if not use_datasets:
        if not args.urls_file:
            logger.error("--urls-file is required unless --apify-dataset-ids is given")
            sys.exit(2)
        urls = read_urls_file(args.urls_file)
        handles = urls_to_handles(urls)
    else:
        handles = []  # populated from dataset posts later

    if args.dry_run and handles:
        handles = handles[:1]

    if not use_datasets and not handles:
        logger.warning(f"No valid handles found in {args.urls_file}; exiting.")
        sys.exit(0)

    processor = EventProcessor(
        concurrency=5,
        school=args.school,
        dry_run=args.dry_run,
        model=args.model,
    )

    posts: list[dict] = []
    if use_datasets:
        for ds_id in dataset_ids:
            ds_posts = fetch_apify_dataset(ds_id)
            logger.info(f"Dataset {ds_id}: returned {len(ds_posts)} items")
            posts.extend(ds_posts)
        # Derive handles from dataset for ScrapeRun bookkeeping
        handles = sorted({(p.get("ownerUsername") or "").strip() for p in posts if p.get("ownerUsername")})
        if args.dry_run:
            handles = handles[:1]
    else:
        scraper = InstagramScraper()
        chunks = [
            handles[i : i + HANDLES_PER_APIFY_RUN]
            for i in range(0, len(handles), HANDLES_PER_APIFY_RUN)
        ]
        for i, chunk in enumerate(chunks, start=1):
            logger.info(f"Apify chunk {i}/{len(chunks)}: scraping {len(chunk)} accounts")
            chunk_posts = scraper.scrape(
                chunk, results_limit=args.limit, cutoff_days=args.cutoff_days
            )
            logger.info(
                f"Apify chunk {i}/{len(chunks)}: returned {len(chunk_posts)} posts"
            )
            posts.extend(chunk_posts)

    scrape_runs: dict[str, ScrapeRun] = {}
    if args.dry_run:
        logger.info("[DRY-RUN] Skipping ScrapeRun row creation; no DB writes will occur.")
    else:
        github_run_id = os.getenv("GITHUB_RUN_ID")
        for username in handles:
            try:
                run = ScrapeRun.objects.create(
                    ig_username=username,
                    github_run_id=github_run_id,
                )
                scrape_runs[username] = run
            except Exception as e:
                logger.warning(f"Failed to create ScrapeRun for {username}: {e}")

    raw_path = Path(__file__).parent / "apify_raw_results.json"
    with raw_path.open("w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    for username, run in scrape_runs.items():
        try:
            user_posts = [p for p in posts if p.get("ownerUsername") == username]
            run.posts_fetched = len(user_posts)
            run.save(update_fields=["posts_fetched"])
        except Exception as e:
            logger.warning(f"Failed to update posts_fetched for {username}: {e}")

    pinned_returned = any(bool(item.get("isPinned")) for item in posts)
    if pinned_returned:
        for run in scrape_runs.values():
            try:
                run.pinned_post_warning = True
                run.save(update_fields=["pinned_post_warning"])
            except Exception:
                pass

    posts = filter_valid_posts(posts)
    if not posts:
        logger.info("No posts retrieved. Exiting.")
        for run in scrape_runs.values():
            try:
                run.status = "no_posts"
                run.finished_at = timezone.now()
                run.save(update_fields=["status", "finished_at"])
            except Exception:
                pass
        sys.exit(0)

    cutoff_date = timezone.now() - timedelta(days=args.cutoff_days)

    try:
        saved_count = asyncio.run(
            processor.process(posts, cutoff_date, scrape_runs=scrape_runs)
        )
        for run in scrape_runs.values():
            try:
                run.status = "success" if run.events_saved > 0 else "no_posts"
                run.finished_at = timezone.now()
                run.save(update_fields=["status", "finished_at"])
            except Exception:
                pass

        if args.dry_run:
            logger.info(
                f"[DRY-RUN] Would have saved {saved_count} event(s) for {args.school} (no DB writes)"
            )
        elif saved_count > 0:
            logger.info(f"Successfully added {saved_count} event(s) for {args.school}")
        else:
            logger.info(f"No new events were added for {args.school}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error in processing: {e}", exc_info=True)
        for run in scrape_runs.values():
            try:
                run.status = "error"
                run.error_message = str(e)
                run.finished_at = timezone.now()
                run.save(update_fields=["status", "error_message", "finished_at"])
            except Exception:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()
