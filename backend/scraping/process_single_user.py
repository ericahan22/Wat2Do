import os
import sys
import django

# Setup Django 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from scraping.logging_config import logger
from scraping.instagram_feed import run_apify_scraper, process_scraped_posts
from django.utils import timezone
from datetime import timedelta


def main():
    target_user = os.environ.get("TARGET_USERNAME")
    if not target_user:
        logger.error("No TARGET_USERNAME provided.")
        sys.exit(1)

    posts_data = run_apify_scraper(username=target_user)
    if not posts_data:
        logger.warning("No posts found.")
        return

    cutoff_date = timezone.now() - timedelta(days=2)
    import asyncio
    try:
        asyncio.run(process_scraped_posts(posts_data, cutoff_date))
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
