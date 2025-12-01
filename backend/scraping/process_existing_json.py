import asyncio
import json
import os
import sys
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from scraping.event_processor import EventProcessor
from scraping.logging_config import logger


def filter_valid_posts(posts):
    return [
        post
        for post in posts
        if not post.get("error")
        and not post.get("errorDescription")
        and post.get("url")
        and "/p/" in post.get("url")
    ]


def main():
    # Get JSON file path from command line argument
    if len(sys.argv) < 2:
        print("Usage: python process_existing_json.py <path_to_json_file>")
        sys.exit(1)

    json_file = Path(sys.argv[1])
    
    if not json_file.exists():
        logger.error(f"JSON file not found: {json_file}")
        sys.exit(1)

    logger.info(f"Loading posts from {json_file}")
    
    with json_file.open("r", encoding="utf-8") as f:
        posts = json.load(f)

    logger.info(f"Loaded {len(posts)} posts from JSON file")

    posts = filter_valid_posts(posts)
    logger.info(f"Filtered to {len(posts)} valid posts")

    if not posts:
        logger.info("No valid posts to process. Exiting.")
        sys.exit(0)

    # Process with EventProcessor in big_scrape mode
    processor = EventProcessor(concurrency=20, big_scrape=True)
    
    # Use Sep 1, 2025 as cutoff
    sep_1 = datetime(2025, 9, 1, tzinfo=dt_timezone.utc)

    # Chunk posts into batches of 50
    batch_size = 50
    total_saved = 0
    
    for i in range(0, len(posts), batch_size):
        batch = posts[i : i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1}/{(len(posts) + batch_size - 1) // batch_size} ({len(batch)} posts)")
        
        try:
            saved_count = asyncio.run(processor.process(batch, sep_1))
            total_saved += saved_count
        except Exception as e:
            logger.error(f"Error processing batch starting at index {i}: {e}")
            logger.error("Stopping processing due to error.")
            sys.exit(1)

    logger.info(f"Successfully processed {total_saved} events in total")


if __name__ == "__main__":
    main()
