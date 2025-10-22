import os
import sys
from dateutil import parser as date_parser
from datetime import datetime, timezone, date, time
from pathlib import Path

from dotenv import load_dotenv
from logging_config import logger

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import events_utils

load_dotenv()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "config.settings.development"),
)


def format_value(value):
    """Format values for TypeScript file"""
    if value is None:
        return "null"
    if isinstance(value, date | time | datetime):
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

    events_list = []
    try:
        from apps.events.models import Events as EventsModel
    except Exception:
        logger.exception("Failed to import Event model")
        return []

    try:
        today = date.today()
        qs = EventsModel.objects.filter(dtstart__date__gte=today).order_by("dtstart")
        for e in qs:
            events_list.append(
                {
                    "id": getattr(e, "id", None),
                    "title": getattr(e, "title", None),
                    "description": getattr(e, "description", None),
                    "location": getattr(e, "location", None),
                    "dtstart": getattr(e, "dtstart", None),
                    "dtend": getattr(e, "dtend", None),
                    "source_url": getattr(e, "source_url", None),
                    "source_image_url": getattr(e, "source_image_url", None),
                    "food": getattr(e, "food", None),
                    "registration": getattr(e, "registration", None),
                    "added_at": getattr(e, "added_at", None),
                    "price": getattr(e, "price", None),
                    "school": getattr(e, "school", None),
                    "club_type": getattr(e, "club_type", None),
                    "ig_handle": getattr(e, "ig_handle", None),
                    "discord_handle": getattr(e, "discord_handle", None),
                    "x_handle": getattr(e, "x_handle", None),
                    "tiktok_handle": getattr(e, "tiktok_handle", None),
                    "fb_handle": getattr(e, "fb_handle", None),
                    "display_handle": events_utils.determine_display_handle(e),
                }
            )
        logger.info(f"Fetched {len(events_list)} events via ORM")
        return events_list
    except Exception as e:
        logger.exception(f"Unexpected error when fetching all events: {e}")
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
                event_id = event["id"]
                f.write("  {\n")
                f.write(f"    id: {format_value(event_id)},\n")
                f.write(f'    ig_handle: {format_value(event["ig_handle"])},\n')
                f.write(f'    source_url: {format_value(event["source_url"])},\n')
                f.write(f'    title: {format_value(event["title"])},\n')
                f.write(f'    dtstart: {format_value(event["dtstart"])},\n')
                f.write(f'    dtend: {format_value(event["dtend"])},\n')
                f.write(f'    location: {format_value(event["location"])},\n')
                f.write(f'    price: {format_value(event["price"])},\n')
                f.write(f'    food: {format_value(event["food"])},\n')
                f.write(f'    registration: {format_value(event["registration"])},\n')
                f.write(
                    f'    source_image_url: {format_value(event["source_image_url"])},\n'
                )
                f.write(f'    club_type: {format_value(event["club_type"])},\n')
                f.write(f'    added_at: {format_value(event["added_at"])},\n')
                f.write(f'    description: {format_value(event["description"])},\n')
                f.write(f'    school: {format_value(event["school"])},\n')
                f.write(
                    f'    discord_handle: {format_value(event["discord_handle"])},\n'
                )
                f.write(f'    x_handle: {format_value(event["x_handle"])},\n')
                f.write(f'    tiktok_handle: {format_value(event["tiktok_handle"])},\n')
                f.write(f'    fb_handle: {format_value(event["fb_handle"])},\n')
                f.write(
                    f'    display_handle: {format_value(event["display_handle"])},\n'
                )
                f.write("  }")
                if i < len(events) - 1:
                    f.write(",")
                f.write("\n")
            f.write("];\n\n")

            # Write recommended filters (now 3D array format)
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
            "Successfully updated staticData.ts with events and recommended filters"
        )

        # --- Static RSS file ---
        try:
            public_dir = output_path.parents[2] / "public"
            public_dir.mkdir(parents=True, exist_ok=True)
            rss_path = public_dir / "rss.xml"

            site_url = "https://wat2do.ca"
            last_build_dt = datetime.now(timezone.utc)

            def parse_dt_to_utc(val):
                dt = val
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)

            rss_items = []
            for ev in events:
                pub_dt = ev.get("dtstart") or ev.get("added_at") or last_build_dt
                pub_dt_parsed = parse_dt_to_utc(pub_dt) or last_build_dt
                pub_str = pub_dt_parsed.strftime("%a, %d %b %Y %H:%M:%S GMT")

                title = ev.get("title").replace("&", "&amp;")
                link = ev.get("source_url").replace("&", "&amp;")
                description = ev.get("description") or ""
                guid = f"{ev.get('id')}@wat2do"
                image_tag = ""
                if ev.get("source_image_url"):
                    image_tag = f'<media:content url="{ev.get("source_image_url")}" medium="image" />'

                item_xml = f"""  <item>
    <title>{title}</title>
    <link>{link}</link>
    <description><![CDATA[{description}]]></description>
    <guid isPermaLink="false">{guid}</guid>
    <pubDate>{pub_str}</pubDate>
    {image_tag}
  </item>
"""
                rss_items.append(item_xml)

            last_build_http = last_build_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
            rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Wat2Do — Upcoming events</title>
    <link>{site_url}</link>
    <atom:link href="{site_url}/rss.xml" rel="self" type="application/rss+xml" />
    <description>Upcoming events at the University of Waterloo</description>
    <lastBuildDate>{last_build_http}</lastBuildDate>
    <ttl>10</ttl>
{''.join(rss_items)}
  </channel>
</rss>
"""
            rss_path.write_text(rss_content, encoding="utf-8")
            logger.info(f"Wrote static RSS feed to {rss_path}")
        except Exception:
            logger.exception("Failed to write static rss.xml")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
