import asyncio
import csv
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


async def process_posts(posts, sep_1):
    processor = EventProcessor(concurrency=5, big_scrape=True)
    
    total_saved = 0
    batch_size = 50
    
    for i in range(0, len(posts), batch_size):
        batch = posts[i : i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1}/{(len(posts) + batch_size - 1) // batch_size} ({len(batch)} posts)")
        
        try:
            # Process batch using existing processor instance
            saved_count = await processor.process(batch, sep_1)
            total_saved += saved_count
            
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Error processing batch starting at index {i}: {e}")
            # Continue to next batch
            continue

    return total_saved


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
    logger.info(f"Found {len(posts)} valid posts to process")

    # Use Sep 1, 2025 as cutoff
    sep_1 = datetime(2025, 9, 1, tzinfo=dt_timezone.utc)

    try:
        total_saved = asyncio.run(process_posts(posts, sep_1))
        logger.info(f"Successfully processed {total_saved} events in total")
    except Exception as e:
        logger.error(f"Critical error in processing: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
