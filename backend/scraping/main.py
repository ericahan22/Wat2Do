import os
import sys
import asyncio
from datetime import timedelta

# 1. Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.utils import timezone
from scraping.apify_client import run_apify_scraper
from scraping.post_processing import process_scraped_posts
from scraping.logging_config import logger
from shared.constants.urls_to_scrape import FULL_URLS

def get_scrape_mode():
    username = os.getenv("TARGET_USERNAME")
    if username:
        return "single", [username]
    
    return "batch", [
        url.split("instagram.com/")[1].split("/")[0]
        for url in FULL_URLS
        if "instagram.com/" in url
    ]

def main():
    mode, usernames = get_scrape_mode()
    logger.info(f"--- Starting Scrape: {mode.upper()} ---")
    
    cutoff_date = timezone.now() - timedelta(days=1)
    
    if mode == "single":
        # Only latest post
        posts_data = run_apify_scraper(usernames[0], results_limit=1)
    else:
        posts_data = run_apify_scraper(usernames)

    if not posts_data:
        logger.warning("No posts returned from Apify.")
        sys.exit(0)

    logger.info("Starting processing...")
    try:
        asyncio.run(process_scraped_posts(posts_data, cutoff_date))
        logger.info("Workflow complete.")
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
