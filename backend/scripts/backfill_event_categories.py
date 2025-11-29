import concurrent.futures
import os
import sys
import threading

import django
import openai

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.events.models import Events
from shared.constants.event_categories import EVENT_CATEGORIES

DEFAULT_CATEGORY = "Uncategorized"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

CATEGORY_LIST = "\n".join(f"- {cat}" for cat in EVENT_CATEGORIES)
lock = threading.Lock()  # For Django ORM thread safety


def get_categories_from_openai(title, description, event_id=None):
    prompt = (
        f"Given the following event title and description, select all applicable categories from this list (output as a JSON array of strings, case-sensitive, must use only these):\n"
        f"{CATEGORY_LIST}\n\n"
        f"Title: {title}\n"
        f"Description: {description}\n\n"
        f"Return a JSON array of one or more categories. If none fit, return ['{DEFAULT_CATEGORY}']."
    )
    try:
        print(f"[{event_id}] Requesting categories from OpenAI...")
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert event classifier."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=64,
            temperature=0,
        )
        content = response.choices[0].message.content.strip()
        print(f"[{event_id}] OpenAI response: {content}")
        if content.startswith("```"):
            content = (
                content.split("```")[-2].strip()
                if "```" in content[3:]
                else content.replace("```json", "").replace("```", "").strip()
            )
        import json

        cats = json.loads(content)
        if isinstance(cats, list) and all(isinstance(c, str) for c in cats):
            valid_cats = [c for c in cats if c in EVENT_CATEGORIES]
            if valid_cats:
                print(f"[{event_id}] Valid categories: {valid_cats}")
                return valid_cats
            else:
                print(
                    f"[{event_id}] No valid categories found in response, using default."
                )
    except Exception as e:
        print(f"[{event_id}] OpenAI error: {e}")
    return [DEFAULT_CATEGORY]


def process_event(event):
    title = event.title or ""
    description = event.description or ""
    print(f"\nProcessing event (ID: {event.id})")
    print(f"[{event.id}] Title: {title}")
    print(
        f"[{event.id}] Description: {description[:100]}{'...' if len(description) > 100 else ''}"
    )
    cats = get_categories_from_openai(title, description, event_id=event.id)
    with lock:
        if event.categories != cats:
            print(f"[{event.id}] Updating categories from {event.categories} to {cats}")
            event.categories = cats
            event.save(update_fields=["categories"])
            print(f"[{event.id}] Updated successfully.")
            return 1
        else:
            print(f"[{event.id}] Categories already up to date.")
            return 0


def main():
    print("Starting event category backfill (only uncategorized events)...")
    events = list(Events.objects.filter(categories=[DEFAULT_CATEGORY]))
    print(f"Found {len(events)} uncategorized events to process.")
    updated = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_event, events))
        updated = sum(results)
    print(
        f"\nDone. Updated {updated} out of {len(events)} uncategorized events with OpenAI-categorized categories."
    )


if __name__ == "__main__":
    main()
