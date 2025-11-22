"""
Account Rotation System
This script implements smart account rotation to reduce Apify credits while
maintaining full event coverage.

Usage:
    python backend/scraping/main_rotated.py

How it works:
    - Splits accounts into 3 groups
    - Group A: Scraped on Mon, Thu, Sun
    - Group B: Scraped on Tue, Fri
    - Group C: Scraped on Wed, Sat
    - Each account checked 2-3x per week
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from scraping.event_processor import EventProcessor
from scraping.instagram_scraper import InstagramScraper
from django.utils import timezone

from scraping.logging_config import logger
from shared.constants.urls_to_scrape import FULL_URLS


def get_rotation_group():
    """
    Determine which group of accounts to scrape based on day of week.
    Returns: (group_name, account_indices)
    """
    day_of_week = datetime.now().weekday()  # 0=Monday, 6=Sunday
    
    # Group A: Monday (0), Thursday (3), Sunday (6)
    # Group B: Tuesday (1), Friday (4)
    # Group C: Wednesday (2), Saturday (5)
    
    rotation_schedule = {
        0: ("A", 0),  # Monday -> Group A
        1: ("B", 1),  # Tuesday -> Group B
        2: ("C", 2),  # Wednesday -> Group C
        3: ("A", 0),  # Thursday -> Group A
        4: ("B", 1),  # Friday -> Group B
        5: ("C", 2),  # Saturday -> Group C
        6: ("A", 0),  # Sunday -> Group A
    }
    
    return rotation_schedule[day_of_week]


def split_accounts_into_groups(accounts, num_groups=3):
    """
    Split accounts into N groups evenly.
    Returns: list of lists
    """
    groups = [[] for _ in range(num_groups)]
    for i, account in enumerate(accounts):
        groups[i % num_groups].append(account)
    return groups


def get_targets():
    """
    Get Instagram accounts to scrape based on rotation schedule.
    """
    username = os.getenv("TARGET_USERNAME")
    if username:
        # Single user mode - no rotation
        return "single", [username]
    
    # Get all Instagram accounts
    all_accounts = [
        url.split("instagram.com/")[1].split("/")[0]
        for url in FULL_URLS
        if "instagram.com/" in url
    ]
    
    # Split into groups
    groups = split_accounts_into_groups(all_accounts, num_groups=3)
    
    # Get today's group
    group_name, group_index = get_rotation_group()
    today_accounts = groups[group_index]
    
    logger.info(f"Rotation Group {group_name} ({len(today_accounts)}/{len(all_accounts)} accounts)")
    
    return "rotated", today_accounts


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
        # Rotated mode: 5 days lookback, 1 post per account
        posts = scraper.scrape(targets, results_limit=1, cutoff_days=5)

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

        if saved_count > 0:
            logger.info(f"Successfully added {saved_count} event(s)")
            sys.exit(0)
        else:
            logger.info("No new events were added")
            sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error in processing: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
