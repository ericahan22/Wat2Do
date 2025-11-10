"""
OpenAI service for AI-powered text analysis and embeddings.

This module provides methods for interacting with OpenAI's API, including:
- Text embeddings generation
- Event information extraction from social media captions
- Image analysis for event data
"""

import json
import os
import traceback
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI
from pytz import timezone as pytz_timezone

from scraping.logging_config import logger
from shared.constants.event_categories import EVENT_CATEGORIES
from utils.date_utils import get_current_semester_end_time


class OpenAIService:
    def __init__(self):
        load_dotenv()
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client only when needed."""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                print("Warning: OPENAI_API_KEY not set. OpenAI functionality will be limited.")
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")
            self.client = None

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector for text using OpenAI's text-embedding-3-small model (1536 dimensions).
        """
        if not text:
            return None

        if not self.client:
            print("Warning: OpenAI client not available. Returning empty embedding.")
            return [0.0] * 1536

        # Clean up the text for better embedding quality
        text = text.replace("\n", " ").replace("\r", " ").strip()

        import re

        text = re.sub(r"\s+", " ")

        try:
            response = self.client.embeddings.create(
                input=[text], model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    def generate_event_embedding(self, event) -> list[float]:
        """
        Generate embedding for an event using a rich text representation.
        This combines multiple event fields to create semantic context.
        """
        # Define field names to include
        field_names = [
            "title",
            "description",
            "location",
            "club_type",
            "ig_handle",
            "dtstart",
            "dtend",
            "food",
            "price",
            "registration",
        ]

        parts = []
        for field_name in field_names:
            value = getattr(event, field_name, None)
            if value:
                parts.append(f"{field_name}: {value}")

        enhanced_text = " | ".join(parts)
        return self.generate_embedding(enhanced_text)

    def extract_events_from_caption(
        self,
        caption_text: str | None = None,
        source_image_url: str | None = None,
        post_created_at: datetime | None = None,
        school: str = "University of Waterloo",
        model: str = "gpt-5-mini",
    ) -> list[dict[str, str | bool | float | None]]:
        """Extract ZERO OR MORE events from caption text/image.

        - Return an array of JSON objects, each object representing a unique event. 
        """
        # Get current date and day of week for context
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_day_of_week = now.strftime("%A")

        # Use post creation time if provided, otherwise use current time
        context_datetime = post_created_at if post_created_at else now
        context_datetime = pytz_timezone("America/Toronto").localize(context_datetime.replace(tzinfo=None))
        context_date = context_datetime.strftime("%Y-%m-%d")
        context_day = context_datetime.strftime("%A")
        context_time = context_datetime.strftime("%H:%M")

        semester_end_time = get_current_semester_end_time(school)
        categories_str = "\n".join(f"- {cat}" for cat in EVENT_CATEGORIES)

        prompt = f"""
    Analyze the following Instagram caption and image and extract event information if it's an event post.

    School context: This post is from {school}. Use this to guide location and timezone decisions.
    Current context: Today is {current_day_of_week}, {current_date}
    Post was created on: {context_day}, {context_date} at {context_time}
    Current semester end date: {semester_end_time}

    Caption: {caption_text}

    STRICT CONTENT POLICY:
    - ONLY extract an event if the post is clearly announcing or describing a real-world event with BOTH:
        * a specific date (e.g., "October 31", "Friday", "tomorrow")
        * AND a specific start time (e.g., "at 2pm", "from 10am-4pm", "noon", "evening").
    - DO NOT extract an event if there is no explicit mention of a start time. Do NOT default to midnight or any other time if none is given.
    - DO NOT extract an event if:
        * The post is a meme, personal photo dump, or generic post with no time/place.
        * The post is inappropriate (nudity, explicit sexual content, or graphic violence).
        * There is no explicit mention of BOTH a date (e.g., "October 31", "Friday", "tomorrow") AND a time (e.g., "at 2pm", "from 10am-4pm", "noon", "evening") in the caption or image.
        * The post only introduces people or some topic, UNLESS there is a clear call to attend or participate in an actual event (such as a meeting, workshop, performance, or competition).

    If you determine that there is NO event in the post, return the JSON value: null (not an object, not an array, just the literal null). Otherwise, return an array of JSON objects with ALL of the following fields:
    {{
        "title": string,
        "description": string,
        "location": string,
        "latitude": number or null,
        "longitude": number or null,
        "price": number or null,
        "food": string,
        "registration": boolean,
        "occurrences": [
            {{
                "dtstart_utc": string,  // UTC start "YYYY-MM-DDTHH:MM:SSZ"
                "dtend_utc": string,    // UTC end "YYYY-MM-DDTHH:MM:SSZ" or empty string if unknown
                "duration": string,   // "HH:MM:SS" or empty string if unknown
                "tz": string          // Timezone name like "America/Toronto"; use the post's timezone context
            }}
        ],
        "school": string,
        "source_image_url": string,
        "categories": list            // one or more of the following, as a JSON array of strings: {categories_str}
    }}

    OCCURRENCE RULES (CRITICAL):
    - Every event MUST include at least one occurrence with a concrete UTC start time.
    - Return ALL explicit dates and times mentioned in the post as separate entries in the occurrences array.
    - Do NOT infer or compress recurrence patterns. List each date/time exactly as given.
    - Always convert local times to UTC. The JSON must use ISO 8601 format with a trailing "Z" (e.g., "2025-11-05T22:00:00Z").
    - If an end time is not provided, leave "dtend_utc" as an empty string.
    - If duration is not explicitly available, leave "duration" as an empty string.
    - Use the timezone context from the caption/image (default to "America/Toronto" for {school}) for the "tz" field.

    ADDITIONAL RULES:
    - Prioritize caption text; use image text if missing details.
    - Title-case event titles.
    - If year not found, assume {now.year}. If end time < start time (e.g., 7pm-12am), set end to the next day.
    - When no explicit date is found but there are relative terms like "tonight", "tomorrow", use the current date context and the date the post was made to determine the date.
    - For location: Use the exact location as stated in the caption or image. If the location is a building or room on campus, use only that (e.g., "SLC 3223", "DC Library"). Include city/province if the event is off-campus and the address is provided.
    - For latitude/longitude: attempt to geocode the location if it's a specific address or well-known place (e.g., "DC Library"). Otherwise, attempt geocoding using the school context. Use null if location is too vague or cannot be geocoded.
    - For price: this represents REGISTRATION COST ONLY. When multiple prices are mentioned, prefer the price that applies to NON-MEMBERS (or general admission). Rules:
        * If both "non-member" / "general admission" and "member" prices appear, use the non-member/general admission numeric price.
        * If only member prices are given and non-member price is absent, use the listed member price.
        * If multiple ticket tiers are listed (e.g., "early bird" and "regular"), use the lowest applicable price (e.g., early bird price).
        * Parse dollar amounts and return a numeric value (e.g., "$15" -> 15.0). Use null for free events or when no price is mentioned.
    - For food: Only set this field if the post says food or drinks will be served, provided, or available for attendees. If specific food or beverage items are mentioned (e.g., "pizza", "bubble tea", "snacks"), list them separated by commas and capitalize ONLY the first item. If the post explicitly says food is provided but does not specify what kind (e.g., "free food", "food provided", "there will be food"), output "Yes!" (exactly). If there is no mention of food or drinks, output an empty string "".
    - For registration: only set to true if there is a clear instruction to register, RSVP, or sign up, otherwise set to false.
    - For description: Make this the caption text word-for-word. If there is no caption text, use the image text.
    - If information is not available, use empty string for strings, null for price/coordinates, and false for booleans.
    - Return ONLY the JSON array text, no extra commentary.
        {f"- An image is provided at: {source_image_url}. If there are conflicts between caption and image information, prioritize the caption text." if source_image_url else ""}
    """

        try:
            logger.debug(
                f"Parsing caption of length: {len(caption_text) if caption_text else 0}"
            )
            if caption_text:
                logger.debug(f"Caption preview: {caption_text[:100]}...")

            # Prepare messages for the API call
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts event information from social media posts. Always return valid JSON with the exact structure requested.",
                },
                {"role": "user", "content": [{"type": "text", "text": prompt}]},
            ]

            # Add image to the message if provided
            if source_image_url:
                logger.debug(f"Including image analysis from: {source_image_url}")
                messages[1]["content"].append(
                    {"type": "image_url", "image_url": {"url": source_image_url}}
                )

            try:
                response = self.client.chat.completions.create(
                    model=model, messages=messages
                )
            except Exception as e:
                logger.exception(f"OpenAI API call failed: {e}")
                return []

            # Extract the JSON response
            response_text = response.choices[0].message.content.strip()

            # Try to parse the JSON response
            try:
                # Remove any markdown formatting if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]

                parsed = json.loads(response_text.strip())

                # Normalize to a list of dicts
                events_list = parsed if isinstance(parsed, list) else []

                cleaned_events: list[dict] = []
                required_fields = [
                    "title",
                    "description",
                    "location",
                    "latitude",
                    "longitude",
                    "price",
                    "food",
                    "registration",
                    "school",
                    "source_image_url",
                    "categories",
                    "occurrences",
                ]

                for event_obj in events_list:
                    for field in required_fields:
                        if field not in event_obj:
                            if field in ["price", "latitude", "longitude"]:
                                event_obj[field] = None
                            elif field in ["registration"]:
                                event_obj[field] = False
                            elif field == "categories":
                                event_obj[field] = []
                            elif field == "occurrences":
                                event_obj[field] = []
                            else:
                                event_obj[field] = ""

                    if source_image_url and not event_obj.get("source_image_url"):
                        event_obj["source_image_url"] = source_image_url

                    if not isinstance(event_obj.get("categories"), list):
                        event_obj["categories"] = [str(event_obj["categories"])] if event_obj["categories"] else []

                    occurrences = event_obj.get("occurrences") or []
                    cleaned_occurrences: list[dict] = []

                    if isinstance(occurrences, list):
                        for occ in occurrences:
                            if not isinstance(occ, dict):
                                continue

                            duration_val = occ.get("duration", "")
                            tz_val = occ.get("tz", "")
                            dtstart_utc = occ.get("dtstart_utc", "")
                            dtend_utc = occ.get("dtend_utc", "")

                            cleaned_occurrences.append(
                                {
                                    "dtstart_utc": dtstart_utc,
                                    "dtend_utc": dtend_utc,
                                    "duration": duration_val,
                                    "tz": tz_val,
                                }
                            )

                    cleaned_occurrences.sort(key=lambda item: item.get("dtstart_utc", ""))
                    event_obj["occurrences"] = cleaned_occurrences

                    cleaned_events.append(event_obj)

                return cleaned_events

            except json.JSONDecodeError:
                logger.exception("Error parsing JSON response")
                logger.error(f"Response text: {response_text}")
                # Return empty list if JSON parsing fails
                return []

        except Exception:
            logger.exception("Error parsing caption")
            logger.error(f"Caption text: {caption_text}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Return empty list if API call fails
            return []

# Singleton instance
openai_service = OpenAIService()


# Backward compatibility - export functions that use the singleton
generate_embedding = openai_service.generate_embedding
extract_events_from_caption = openai_service.extract_events_from_caption
generate_event_embedding = openai_service.generate_event_embedding
