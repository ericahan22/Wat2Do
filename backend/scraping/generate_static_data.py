import os
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path
from logging_config import logger

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "config.settings.development")
)


def format_value(value):
    """Format values for TypeScript file"""
    if value is None:
        return "null"
    if isinstance(value, (date, time, datetime)):
        return f'"{value.isoformat()}"'
    if isinstance(value, str):
        escaped_value = (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )
        return f'"{escaped_value}"'
    if isinstance(value, bool):
        return str(value).lower()
    return value


def fetch_events():
    """Fetch all upcoming events from the database for static data generation"""
    try:
        import django
        django.setup()
    except Exception:
        logger.exception("Failed to setup Django before importing models")
        return []
    
    from django.db import connection, ProgrammingError, OperationalError

    try:
        tables = connection.introspection.table_names()
    except Exception:
        tables = []
    use_new_table = "events_event" in tables
    legacy_table = "events" in tables or "public.events" in tables
    if not use_new_table and not legacy_table:
        logger.warning("No events table found in DB")
        return []
    
    events_list = []
    if use_new_table:
        try:
            from apps.events.models import Event as EventsModel  # new model
        except Exception:
            logger.exception("Failed to import Event model")
            return []
        try:
            today = date.today()
            qs = EventsModel.objects.filter(utc_start_ts__date__gte=today).order_by("utc_start_ts")
            for e in qs:
                events_list.append(
                    {
                        "id": getattr(e, "id", None),
                        "club_handle": getattr(e, "ig_handle", None),
                        "url": getattr(e, "source_url", None),
                        "name": getattr(e, "title", None),
                        "date": getattr(e, "dtstart", None),
                        "start_time": getattr(e, "dtstart", None),
                        "end_time": getattr(e, "dtend", None),
                        "location": getattr(e, "location", None),
                        "price": getattr(e, "price", None),
                        "food": getattr(e, "food", None),
                        "registration": getattr(e, "registration", None),
                        "image_url": getattr(e, "source_image_url", None),
                        "club_type": getattr(e, "club_type", None),
                        "added_at": getattr(e, "added_at", None),
                        "description": getattr(e, "description", None),
                    }
                )
            logger.info(f"Fetched {len(events_list)} events via ORM")
            return events_list
        except (ProgrammingError, OperationalError) as db_err:
            logger.error(f"ORM query failed: {db_err}")
            return []
        except Exception:
            logger.exception("Unexpected error with ORM fetch")
            return []

    # Raw SQL
    try:
        today = date.today()
        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT id, club_handle, url, name, date, start_time, end_time,
                       location, price, food, registration, image_url,
                       description, club_type, added_at
                FROM public.events
                WHERE date >= %s
                ORDER BY date, start_time
                """,
                [today],
            )
            rows = cur.fetchall()
            for r in rows:
                (rid, club_handle, url, name, rdate, start_time, end_time, location, price, food, registration, image_url, description, club_type, added_at) = r
                events_list.append(
                    {
                        "id": rid,
                        "club_handle": club_handle,
                        "url": url,
                        "name": name,
                        "date": rdate,
                        "start_time": start_time,
                        "end_time": end_time,
                        "location": location,
                        "price": price,
                        "food": food,
                        "registration": registration,
                        "image_url": image_url,
                        "club_type": club_type,
                        "added_at": added_at,
                        "description": description,
                    }
                )
        logger.info(f"Fetched {len(events_list)} events via raw SQL")
        return events_list
    except Exception:
        logger.exception("Failed to fetch events via raw SQL")
        return []
    

def generate_recommended_filters(events_data):
    """Generate recommended filters using OpenAI service"""
    try:
        from services.openai_service import generate_recommended_filters

        logger.info("Generating recommended filters using OpenAI...")
        recommended_filters = generate_recommended_filters(events_data)

        if not recommended_filters:
            logger.warning("Failed to generate recommended filters")
            return []

        logger.info(
            f"Generated {len(recommended_filters)} filters: {recommended_filters}"
        )
        return recommended_filters
    except Exception as e:
        logger.error(f"Error generating recommended filters: {e}")
        return []


def main():
    """Fetches events, generates filters, and writes to staticData.ts"""
    try:
        # Fetch upcoming events
        events = fetch_events()

        # Generate recommended filters
        recommended_filters = generate_recommended_filters(events)

        # Write to staticData.ts
        output_path = (
            Path(__file__).parent.parent.parent
            / "frontend"
            / "src"
            / "data"
            / "staticData.ts"
        )
        logger.info(f"Writing to {output_path}...")
        with output_path.open("w", encoding="utf-8") as f:
            # Write the last updated timestamp in UTC
            current_time = datetime.now(timezone.utc).isoformat()
            f.write('import { Event } from "@/features/events/types/events";\n\n')
            f.write(f'export const LAST_UPDATED = "{current_time}";\n\n')

            # Write static events data as an array of Event objects
            f.write("export const staticEventsData: Event[] = [\n")
            for i, event in enumerate(events):
                event_id = str(event["id"])
                f.write("  {\n")
                f.write(f"    id: {format_value(event_id)},\n")
                f.write(f'    club_handle: {format_value(event["club_handle"])},\n')
                f.write(f'    url: {format_value(event["url"])},\n')
                f.write(f'    name: {format_value(event["name"])},\n')
                f.write(f'    date: {format_value(event["date"])},\n')
                f.write(f'    start_time: {format_value(event["start_time"])},\n')
                f.write(f'    end_time: {format_value(event["end_time"])},\n')
                f.write(f'    location: {format_value(event["location"])},\n')
                f.write(f'    price: {format_value(event["price"])},\n')
                f.write(f'    food: {format_value(event["food"])},\n')
                f.write(f'    registration: {format_value(event["registration"])},\n')
                f.write(f'    image_url: {format_value(event["image_url"])},\n')
                f.write(f'    club_type: {format_value(event["club_type"])},\n')
                f.write(f'    added_at: {format_value(event["added_at"])},\n')
                f.write("  }")
                if i < len(events) - 1:
                    f.write(",")
                f.write("\n")
            f.write("];\n\n")

            # Write recommended filters
            if recommended_filters:
                f.write("export const RECOMMENDED_FILTERS: string[] = [\n")
                for i, filter_keyword in enumerate(recommended_filters):
                    escaped = filter_keyword.replace('"', '\\"')
                    f.write(f'  "{escaped}"')
                    if i < len(recommended_filters) - 1:
                        f.write(",")
                    f.write("\n")
                f.write("];\n")
            else:
                f.write("export const RECOMMENDED_FILTERS: string[] = [];\n")

        logger.info(
            "Successfully updated staticData.ts with events and recommended filters"
        )
    except Exception:
        logger.exception("An error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
