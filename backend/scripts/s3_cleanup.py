#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from typing import Set
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.storage_service import delete_images, list_all_s3_objects

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


def get_referenced_s3_keys() -> Set[str]:
    logger.info("Querying events table for referenced image URLs...")

    database_url = os.getenv("DATABASE_URL")

    try:
        conn = psycopg2.connect(database_url)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT image_url FROM events WHERE image_url IS NOT NULL"
            )
            rows = cur.fetchall()

        referenced_keys = set()
        for (image_url,) in rows:
            s3_key = urlparse(image_url).path.lstrip("/")
            if s3_key:
                referenced_keys.add(s3_key)

        logger.info(f"Found {len(referenced_keys)} referenced S3 keys")
        return referenced_keys

    except Exception as e:
        logger.error(f"Error querying database: {e}")
        raise
    finally:
        if "conn" in locals():
            conn.close()


def main():
    parser = argparse.ArgumentParser(description="Clean up unused S3 objects")
    parser.add_argument(
        "--confirm",
        type=lambda x: x.lower() == "true",
        default=False,
        help="If true, actually delete files",
    )

    try:
        referenced_keys = get_referenced_s3_keys()

        all_s3_keys = list_all_s3_objects()

        orphaned_keys = set(all_s3_keys) - referenced_keys

        logger.info(f"Referenced keys: {len(referenced_keys)}")
        logger.info(f"Total S3 objects: {len(all_s3_keys)}")
        logger.info(f"Orphaned objects: {len(orphaned_keys)}")

        if orphaned_keys:
            orphaned_keys_list = sorted(list(orphaned_keys))
            logger.warning("Files will be permanently deleted!")

            deleted_count = delete_images(orphaned_keys_list)
            logger.info(f"CLEANUP COMPLETE: Deleted {deleted_count} orphaned objects")
        else:
            logger.info("No orphaned objects found - S3 bucket is clean!")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
