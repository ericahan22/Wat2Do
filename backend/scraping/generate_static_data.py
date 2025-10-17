import os
import sys
from datetime import date, datetime, time, timezone, timedelta
from pathlib import Path
from logging_config import logger

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


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
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
    try:
        import django
        django.setup()
    except Exception as e:
        logger.error(f"Failed to setup Django: {e}")
        
    try:
        from apps.events.models import Events
        from django.core.exceptions import FieldDoesNotExist
    except Exception as e:
        logger.error(f"Failed to import Events model: {e}")
        
    today = date.today()
    
    use_dtstart = True
    try:
        Events._meta.get_field("dtstart")
    except (FieldDoesNotExist, Exception):
        use_dtstart = False
    
    events_list = []
    if use_dtstart:
        qs = Events.objects.filter(dtstart__date__gte=today).order_by("dtstart", "dtstart")
    else:
        qs = Events.objects.filter(date__gte=today).order_by("date", "start_time")
        
    for e in qs:
        if use_dtstart:
            ev_date = getattr(e, "dtstart", None)
            ev_start = getattr(e, "dtstart", None)
            ev_end = getattr(e, "dtend", None)
            if ev_end is None and ev_start is not None:
                ev_end = ev_start + timedelta(hours=1)
            image_url = getattr(e, "source_image_url", None) or getattr(e, "image_url", None)
            url = getattr(e, "source_url", None) or getattr(e, "url", None)
            name = getattr(e, "title", None) or getattr(e, "name", None)
        else:
            ev_date = getattr(e, "date", None)
            ev_start = getattr(e, "start_time", None)
            ev_end = getattr(e, "end_time", None) or (ev_date + timedelta(hours=1) if isinstance(ev_date, datetime) else None)
            image_url = getattr(e, "image_url", None)
            url = getattr(e, "url", None)
            name = getattr(e, "name", None)
    
        item = {
            "id": getattr(e, "id", None),
            "club_handle": getattr(e, "club_handle", None),
            "url": url,
            "name": name,
            "date": ev_date,
            "start_time": ev_start,
            "end_time": ev_end,
            "location": getattr(e, "location", None),
            "price": getattr(e, "price", None),
            "food": getattr(e, "food", None),
            "registration": getattr(e, "registration", None),
            "image_url": image_url,
            "club_type": getattr(e, "club_type", None),
            "added_at": getattr(e, "added_at", None),
            "description": getattr(e, "description", None)
        }
        events_list.append(item)
        
    logger.info(f"Fetched {len(events_list)} events, use_dtstart={use_dtstart}")
    return events_list


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
