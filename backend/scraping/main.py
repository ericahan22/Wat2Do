import asyncio
import json
import os
import sys
from datetime import timedelta
from pathlib import Path

# 1. Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from scraping.event_processor import EventProcessor
from scraping.instagram_scraper import InstagramScraper
from django.utils import timezone

from scraping.logging_config import logger
from shared.constants.urls_to_scrape import FULL_URLS


def get_targets():
    """
    Determine if we are in 'Single User' mode or 'Batch' mode.
    """
    username = os.getenv("TARGET_USERNAME")
    if username:
        return "single", [username]
    
    batch_users = [
        url.split("instagram.com/")[1].split("/")[0]
        for url in FULL_URLS
        if "instagram.com/" in url
    ]
    return "batch", batch_users

def filter_valid_posts(posts):
    return [
        post for post in posts
        if not post.get("error") and not post.get("errorDescription")
        and post.get("url") and "/p/" in post.get("url")
    ]

def main():
    mode, targets = get_targets()
    logger.info(f"--- Workflow Started: {mode.upper()} ---")
    scraper = InstagramScraper()
    processor = EventProcessor(concurrency=5)

    # Configure run based on mode
    if mode == "single":
        # Single user: 1 day lookback, 1 post limit
        posts = scraper.scrape(targets[0], results_limit=1, cutoff_days=1)
    else:
        # Batch mode: 2 days lookback, 1 post per account
        posts = scraper.scrape(targets, results_limit=1, cutoff_days=2)

    raw_path = Path(__file__).parent / "apify_raw_results.json"
    with raw_path.open("w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    # Filter out results not containing posts before processing
    posts = filter_valid_posts(posts)
    if not posts:
        logger.info("No posts retrieved. Exiting.")
        sys.exit(0)

    cutoff_date = timezone.now() - timedelta(days=1)
    try:
        saved_count = asyncio.run(processor.process(posts, cutoff_date))

        # 0 = success (events added)
        # 2 = warning (no events added)
        # 1 = error (exception occurred)
        if saved_count > 0:
            logger.info(f"Successfully added {saved_count} event(s)")
            sys.exit(0)
        else:
            logger.info("No new events were added")
            sys.exit(2)
    except Exception as e:
        logger.error(f"Critical error in processing: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
