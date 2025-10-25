#!/usr/bin/env python3
"""
Generate recommended filter keywords from upcoming events and update staticData.ts.

This script:
1. Fetches all upcoming events from the database
2. Uses OpenAI to generate relevant filter keywords
3. Updates the frontend staticData.ts file with the new filters
"""

import logging
import os
import re
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.events.models import Events  # noqa: E402
from services.openai_service import generate_recommended_filters  # noqa: E402

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_upcoming_events():
    """Fetch all events with dates >= today"""
    today = date.today()
    logger.info(f"Fetching upcoming events from {today}...")

    events = Events.objects.filter(date__gte=today).values(
        "name", "location", "date", "food", "club_type", "description"
    )

    events_list = list(events)
    logger.info(f"Found {len(events_list)} upcoming events")
    return events_list


def update_static_data_file(recommended_filters):
    """Update the staticData.ts file with new recommended filters"""
    from datetime import datetime, timezone
    
    # Find the frontend staticData.ts file
    frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
    static_data_path = frontend_dir / "src" / "data" / "staticData.ts"

    if not static_data_path.exists():
        logger.error("Could not find staticData.ts")
        return False

    try:
        # Write the complete file with LAST_UPDATED and RECOMMENDED_FILTERS
        with open(static_data_path, "w", encoding="utf-8") as f:
            # Write the last updated timestamp in UTC
            current_time = datetime.now(timezone.utc).isoformat()
            f.write(f'export const LAST_UPDATED = "{current_time}";\n\n')

            # Write recommended filters (3D array format)
            if recommended_filters:
                f.write(
                    "export const RECOMMENDED_FILTERS: [string, string, string][] = [\n"
                )
                for i, filter_item in enumerate(recommended_filters):
                    if len(filter_item) == 3:
                        category, emoji_string, filter_name = filter_item
                        category_escaped = category.replace('"', '\\"')
                        emoji_escaped = emoji_string.replace('"', '\\"')
                        filter_escaped = filter_name.replace('"', '\\"')
                        f.write(
                            f'  ["{category_escaped}", "{emoji_escaped}", "{filter_escaped}"]'
                        )
                        if i < len(recommended_filters) - 1:
                            f.write(",")
                        f.write("\n")
                f.write("];\n")
            else:
                f.write(
                    "export const RECOMMENDED_FILTERS: [string, string, string][] = [];\n"
                )

        logger.info(
            f"✅ Successfully updated {static_data_path.name} with {len(recommended_filters)} filters"
        )
        return True

    except Exception:
        logger.exception("Error updating static data file")
        return False


def main():
    """Main execution flow"""
    logger.info("=" * 60)
    logger.info("Starting recommended filters generation")
    logger.info("=" * 60)

    # Step 1: Fetch upcoming events
    events_data = fetch_upcoming_events()

    if not events_data:
        logger.warning("No upcoming events found, cannot generate filters")
        return 1

    # Step 2: Generate recommended filters using OpenAI
    logger.info("Generating recommended filters using OpenAI...")
    recommended_filters = generate_recommended_filters(events_data)

    if not recommended_filters:
        logger.error("Failed to generate recommended filters")
        return 1

    logger.info(f"Generated {len(recommended_filters)} filters: {recommended_filters}")

    # Step 3: Update the staticData.ts file
    success = update_static_data_file(recommended_filters)

    if success:
        logger.info("=" * 60)
        logger.info("✅ Recommended filters generation completed successfully")
        logger.info("=" * 60)
        return 0
    else:
        logger.error("Failed to update static data file")
        return 1


if __name__ == "__main__":
    sys.exit(main())
