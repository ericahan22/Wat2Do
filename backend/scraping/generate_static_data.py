import os
import sys
from datetime import date, datetime, time, timezone
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
        qs = EventsModel.objects.filter(
            event_dates__dtstart_utc__date__gte=today
        ).order_by("event_dates__dtstart_utc")
        for e in qs:
            events_list.append(
                {
                    "id": getattr(e, "id", None),
                    "title": getattr(e, "title", None),
                    "description": getattr(e, "description", None),
                    "location": getattr(e, "location", None),
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


def main():
    """Fetches events and writes static data files"""
    try:
        # Fetch upcoming events
        events = fetch_events()

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
            f.write(f'export const LAST_UPDATED = "{current_time}";\n\n')

            # Write event emoji categories
            f.write("export const EVENT_EMOJIS_CATEGORIES: [string, string, string][] = [\n")
            emoji_categories = [
                ["Objects", "Graduation%20Cap", "Academic"],
                ["Objects", "Briefcase", "Career & Networking"],
                ["Activity", "Video%20Game", "Social & Games"],
                ["Activity", "Soccer%20Ball", "Athletics"],
                ["Activity", "Artist%20Palette", "Creative Arts"],
                ["Travel%20and%20Places", "Classical%20Building", "Cultural"],
                ["Animals%20and%20Nature", "Dove", "Religious"],
                ["Objects", "Megaphone", "Advocacy & Causes"],
                ["Objects", "Chart%20Increasing", "Sales & Fundraising"]
            ]
            for i, (group, emoji, category) in enumerate(emoji_categories):
                f.write(f'  ["{group}", "{emoji}", "{category}"]')
                if i < len(emoji_categories) - 1:
                    f.write(",")
                f.write("\n")
            f.write("];\n\n")

            # Write event categories
            f.write("export const EVENT_CATEGORIES = [\n")
            categories = [
                "Academic",
                "Career & Networking",
                "Social & Games",
                "Athletics",
                "Creative Arts",
                "Cultural",
                "Religious",
                "Advocacy & Causes",
                "Sales & Fundraising",
            ]
            for i, category in enumerate(categories):
                f.write(f'  "{category}"')
                if i < len(categories) - 1:
                    f.write(",")
                f.write("\n")
            f.write("];\n")

        logger.info("Successfully updated staticData.ts")

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
                pub_dt = (
                    ev.get("event_dates__dtstart_utc")
                    or ev.get("added_at")
                    or last_build_dt
                )
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
