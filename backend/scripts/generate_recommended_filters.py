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
    # Find the frontend staticEvents.ts or staticData.ts file
    frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
    static_events_path = frontend_dir / "src" / "data" / "staticEvents.ts"
    static_data_path = frontend_dir / "src" / "data" / "staticData.ts"

    # Determine which file exists
    if static_data_path.exists():
        target_file = static_data_path
        logger.info(f"Updating existing staticData.ts at {target_file}")
    elif static_events_path.exists():
        target_file = static_events_path
        logger.info(f"Found staticEvents.ts, will update it at {target_file}")
    else:
        logger.error("Could not find staticEvents.ts or staticData.ts")
        return False

    try:
        # Read the current file
        with open(target_file, encoding="utf-8") as f:
            content = f.read()

        # Format the recommended filters as a TypeScript array
        filters_ts = "export const RECOMMENDED_FILTERS: string[] = [\n"
        for filter_keyword in recommended_filters:
            # Escape quotes in the keyword
            escaped = filter_keyword.replace('"', '\\"')
            filters_ts += f'  "{escaped}",\n'
        filters_ts += "];\n"

        # Check if RECOMMENDED_FILTERS already exists
        if "export const RECOMMENDED_FILTERS" in content:
            # Replace existing RECOMMENDED_FILTERS
            pattern = r"export const RECOMMENDED_FILTERS:.*?\];"
            content = re.sub(pattern, filters_ts.rstrip("\n"), content, flags=re.DOTALL)
            logger.info("Updated existing RECOMMENDED_FILTERS")
        else:
            # Append to the end of the file
            content += "\n" + filters_ts
            logger.info("Added new RECOMMENDED_FILTERS export")

        # Write back to the file
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(
            f"✅ Successfully updated {target_file.name} with {len(recommended_filters)} filters"
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
