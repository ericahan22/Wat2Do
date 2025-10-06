import logging
import os
import sys
from datetime import date, datetime, time
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()


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


def main():
    """Connects to Supabase DB, fetches all events, writes to TS file"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    try:
        conn_string = os.environ.get("SUPABASE_DB_URL")
        logging.info("Connecting to the database...")
        with psycopg2.connect(conn_string) as conn, conn.cursor() as cur:
            logging.info("Executing query...")
            query = """
                SELECT
                    e.id,
                    e.club_handle,
                    e.url,
                    e.name,
                    e.date,
                    e.start_time,
                    CASE
                        WHEN e.end_time IS NULL THEN e.start_time + interval '1 hour'
                        ELSE e.end_time
                    END as end_time,
                    e.location,
                    e.price,
                    e.food,
                    e.registration,
                    e.image_url,
                    e.club_type,
                    e.added_at
                FROM
                    events e
                ORDER BY e.date ASC, e.start_time ASC;
                """
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            events = [dict(zip(columns, row, strict=False)) for row in cur.fetchall()]
            logging.info(f"Fetched {len(events)} events.")
        output_path = (
            Path(__file__).parent.parent.parent
            / "frontend"
            / "src"
            / "data"
            / "staticEvents.ts"
        )
        logging.info(f"Writing to {output_path}...")
        with output_path.open("w", encoding="utf-8") as f:
            # Write the last updated timestamp
            current_time = datetime.now().isoformat()
            f.write('import { Event } from "@/hooks/useEvents";\n\n')
            f.write(f'export const LAST_UPDATED = "{current_time}";\n\n')
            f.write("export const staticEventsData = new Map<string, Event>([\n")
            for i, event in enumerate(events):
                event_id = str(event["id"])
                f.write(f"  [{format_value(event_id)}, {{\n")
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
                f.write("  }]")
                if i < len(events) - 1:
                    f.write(",")
                f.write("\n")
            f.write("]);\n")
        logging.info("Successfully updated staticEvents.ts")
    except Exception:
        logging.exception("An error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
