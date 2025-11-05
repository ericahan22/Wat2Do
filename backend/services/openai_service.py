"""
OpenAI service for AI-powered text analysis and embeddings.

This module provides methods for interacting with OpenAI's API, including:
- Text embeddings generation
- Event information extraction from social media captions
- Image analysis for event data
"""

import json
import os
import time
import traceback
from copy import deepcopy
from datetime import datetime
import re
from urllib.parse import urljoin

from dotenv import load_dotenv
from openai import OpenAI

from scraping.logging_config import logger
from shared.constants.emojis import EMOJI_CATEGORIES
from shared.constants.event_categories import EVENT_CATEGORIES
from utils.events_utils import clean_datetime
from utils.date_utils import get_current_semester_end_time
from datetime import timezone as pytimezone


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
        caption_text: str,
        source_image_url: str | None = None,
        post_created_at: datetime | None = None,
        school: str = "University of Waterloo",
    ) -> list[dict[str, str | bool | float | None]]:
        """Extract ZERO OR MORE events from caption text/image.

        - Return an array of JSON objects, each object representing a unique event.
        - If the same event lists multiple dates/times, represent it as a single object
          and use rdate (additional dates) and/or rrule (recurrence rule) appropriately.
        """
        # Get current date and day of week for context
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_day_of_week = now.strftime("%A")

        # Use post creation time if provided, otherwise use current time
        context_datetime = post_created_at if post_created_at else now
        context_date = context_datetime.strftime("%Y-%m-%d")
        context_day = context_datetime.strftime("%A")
        context_time = context_datetime.strftime("%H:%M")

        # Get current semester end time for inferring RRULE UNTIL dates
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
        "dtstart": string,            // local start in "YYYY-MM-DD HH:MM:SS+HH"
        "dtend": string,              // local end in "YYYY-MM-DD HH:MM:SS+HH" or empty string
        "dtstart_utc": string,        // UTC start "YYYY-MM-DD HH:MM:SSZ" or empty string
        "dtend_utc": string,          // UTC end "YYYY-MM-DD HH:MM:SSZ" or empty string
        "duration": string,           // "HH:MM:SS" or empty string
        "all_day": boolean,
        "location": string,
        "latitude": number or null,
        "longitude": number or null,
        "tz": string,
        "price": number or null,
        "food": string,
        "registration": boolean,
        "rrule": string,
        "rdate": string,              // comma-separated datetime strings in format "YYYYMMDDTHHMMSS,YYYYMMDDTHHMMSS,..." (e.g., "20251113T170000,20251204T170000,20251218T170000")
        "school": string,
        "source_image_url": string,
        "description": string,
        "categories": list            // one or more of the following, as a JSON array of strings: {categories_str}
    }}

    CONSOLIDATION RULES (VERY IMPORTANT):
    - If multiple dates/times describe the SAME event (same title/location/content), CONSOLIDATE into ONE object:
        * Put the primary occurrence in dtstart/dtend.
        * For additional dates: use EITHER rdate (for specific dates without a pattern) OR rrule (for a clear recurring pattern like "every Monday").
        * IMPORTANT: Use EITHER rrule OR rdate, NEVER both. If using rdate, set rrule to "". If using rrule, set rdate to "".
        * Never create separate objects for the same event just because of multiple dates.
    - Only create multiple objects when the caption clearly describes DISTINCT events (different titles, venues, or clearly different activities).

    RDATE vs RRULE RULES (CRITICAL):
    
    MUTUAL EXCLUSIVITY (MANDATORY):
    - RRULE and RDATE are MUTUALLY EXCLUSIVE - you must use EITHER one OR the other, NEVER both.
    - If an event has multiple specific dates with NO recurring pattern, use RDATE only (rrule must be "").
    - If an event has a recurring pattern (e.g., "every Monday", "weekly"), use RRULE only (rdate must be "").
    - If an event has no recurrence or additional dates, both rrule and rdate should be empty strings "".
    
    - Use RDATE when multiple specific dates are listed but NO recurring pattern is explicitly stated:
        * Example: "Join us Oct 15, Oct 22, Nov 3, and Nov 10" -> Use RDATE with the additional dates, rrule must be ""
        * RDATE should be a comma-separated string of datetime values in format YYYYMMDDTHHMMSS
        * Example: "20251022T140000,20251103T140000,20251110T140000"
        * Put the first occurrence in dtstart/dtend, remaining dates/times in rdate
        * When using RDATE, always set rrule to ""
    
    - Use RRULE when a recurring pattern IS explicitly stated (e.g., "every Monday", "weekly on Wednesdays", "daily"):
    * DO NOT USE RRULE IF THE EVENT HAS NO RECURRING PATTERN
        * RRULE MUST include the UNTIL parameter to specify when the recurrence ends
        * Format: FREQ=WEEKLY;BYDAY=MO;UNTIL={semester_end_time}
        * If no end date is mentioned, use {semester_end_time} as the UNTIL value
        * Common RRULE examples:
            - Every Wednesday until December: FREQ=WEEKLY;BYDAY=WE;UNTIL=20251130T235959Z
            - Daily for a week: FREQ=DAILY;UNTIL=20251110T235959Z
            - Every Tuesday and Thursday: FREQ=WEEKLY;BYDAY=TU,TH;UNTIL=20251215T235959Z
        * When using RRULE, always set rdate to ""

    MULTIPLE TIME SLOTS FOR SAME RECURRING EVENT:
    When the same event has multiple time slots on the same day(s) of the week, create SEPARATE event objects for each time slot.
    Example: "Weekly sessions every Wednesday: 5-6 PM and 8-10 PM through December"
    Should create TWO event objects:
    [
        {{
            "...": "...",
            "dtstart": "2025-11-05 17:00:00-05",
            "dtend": "2025-11-05 18:00:00-05",
            "dtstart_utc": "2025-11-05 22:00:00Z",
            "dtend_utc": "2025-11-05 23:00:00Z",
            "duration": "01:00:00",
            "all_day": false,
            "rrule": "FREQ=WEEKLY;BYDAY=WE;UNTIL=20251231T235959Z",
            "rdate": "",
        }},
        {{
            "...": "...",
            "dtstart": "2025-11-05 20:00:00-05",
            "dtend": "2025-11-05 22:00:00-05",
            "dtstart_utc": "2025-11-06 01:00:00Z",
            "dtend_utc": "2025-11-06 03:00:00Z",
            "duration": "02:00:00",
            "rrule": "FREQ=WEEKLY;BYDAY=WE;UNTIL=20251231T235959Z",
            "rdate": "",
        }}
    ]
    This represents two separate recurring time slots (5-6 PM and 8-10 PM) on every Wednesday from November through December.

    ADDITIONAL RULES:
    - Prioritize caption text; use image text if missing details.
    - Title-case event titles.
    - If year not found, assume {now.year}. If end time < start time (e.g., 7pm-12am), set end to next day.
    - When no explicit date is found but there are relative terms like "tonight", "tomorrow", use the current date context and the date the post was made to determine the date.
    - Convert local times to UTC using tz for dtstart_utc/dtend_utc when available.
    - For all_day: ONLY set to true if the post **explicitly states** it is an all-day event (e.g., "all day", "full day").
    - For location: Use the exact location as stated in the caption or image. If the location is a building or room on campus, use only that (e.g., "SLC 3223", "DC Library"). Include city/province if the event is off-campus and the address is provided.
    - For latitude/longitude: attempt to geocode the location if it's a specific address or well-known place (e.g., "DC Library"). Otherwise, attempt geocoding using the school context. Use null if location is too vague or cannot be geocoded.
    - For tz mappings, default to "America/Toronto" for {school}.
    - For price: this represents REGISTRATION COST ONLY. When multiple prices are mentioned, prefer the price that applies to NON-MEMBERS (or general admission). Rules:
        * If both "non-member" / "general admission" and "member" prices appear, use the non-member/general admission numeric price.
        * If only member prices are given and non-member price is absent, use the listed member price.
        * If multiple ticket tiers are listed (e.g., "early bird" and "regular"), use the lowest applicable price (e.g., early bird price).
        * Parse dollar amounts and return a numeric value (e.g., "$15" -> 15.0). Use null for free events or when no price is mentioned.
    - For food: Only set this field if the post says food or drinks will be served, provided, or available for attendees. If specific food or beverage items are mentioned (e.g., "pizza", "bubble tea", "snacks"), list them separated by commas and capitalize ONLY the first item. If the post explicitly says food is provided but does not specify what kind (e.g., "free food", "food provided", "there will be food"), output "Yes!" (exactly). If there is no mention of food or drinks, output an empty string "".
    - For registration: only set to true if there is a clear instruction to register, RSVP, or sign up, otherwise set to false.
    - For rrule and rdate: they are MUTUALLY EXCLUSIVE. Use EITHER rrule (for recurring patterns) OR rdate (for specific dates without a pattern), NEVER both. If using rrule, set rdate to "". If using rdate, set rrule to "".
    - For description: start with the caption text word-for-word, then append any additional insights about the event extracted from the image that are not already mentioned in the caption.
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
            model = "gpt-5-mini"

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
                    "dtstart",
                    "dtend",
                    "dtstart_utc",
                    "dtend_utc",
                    "all_day",
                    "tz",
                    "food",
                    "price",
                    "registration",
                    "rrule",
                    "rdate",
                    "school",
                    "source_image_url",
                ]

                for event_obj in events_list:
                    for field in required_fields:
                        if field not in event_obj:
                            if field in ["price", "latitude", "longitude"]:
                                event_obj[field] = None
                            elif field in ["registration", "all_day"]:
                                event_obj[field] = False
                            else:
                                event_obj[field] = ""

                    if source_image_url and not event_obj.get("source_image_url"):
                        event_obj["source_image_url"] = source_image_url

                    # --- Manual UTC conversion for dtstart_utc and dtend_utc ---
                    dtstart = clean_datetime(event_obj.get("dtstart"))
                    dtend = clean_datetime(event_obj.get("dtend"))

                    if dtstart:
                        event_obj["dtstart_utc"] = dtstart.astimezone(pytimezone.utc).isoformat()
                    else:
                        event_obj["dtstart_utc"] = None

                    if dtend:
                        event_obj["dtend_utc"] = dtend.astimezone(pytimezone.utc).isoformat()
                    else:
                        event_obj["dtend_utc"] = None

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

    def generate_recommended_filters(self, events_data: list[dict]) -> list[list[str]]:
        """Generate recommended filter keywords with emojis from upcoming events data using GPT

        Returns a list of 3-element arrays: [category, emoji_string, filter_name]
        """
        if not events_data:
            logger.warning("No events data provided for filter generation")
            return []

        # Prepare event summaries for the prompt
        event_summaries = []
        for event in events_data[:20]:
            title = event.get("title")
            summary = f"- {title}"
            event_summaries.append(summary)

        # Get the categorized emoji list for the prompt
        emoji_categories = EMOJI_CATEGORIES
        emoji_list_str = ""
        for category, emojis in emoji_categories.items():
            emoji_list_str += f"\n{category}:\n"
            emoji_list_str += ", ".join(emojis) + "\n"

        prompt = f"""
Analyze the following list of {len(event_summaries)} upcoming student event titles and generate 20-25 search filter keywords with matching emojis.

Event titles:
{chr(10).join(event_summaries)}

Available emojis organized by category (select the most fitting one for each filter):
{emoji_list_str}

IMPORTANT: You MUST use ONLY the emoji categories listed above (Smileys, People, Animals and Nature, Food and Drink, Activity, Travel and Places, Objects, Symbols, Flags). Do NOT use club types like "WUSA", "Student Society", or "Athletics" as categories - these are not emoji categories.

Generate filter keywords that:
1. Are derived ONLY from words and themes present in the event TITLES above. Ignore captions, descriptions, locations, and food mentions.
2. Are SHORT (1-3 words max) and SPECIFIC.
3. Reflect common themes that actually appear in multiple titles.
4. The filter string MUST exist verbatim in at least 3 event titles above.

For each filter, select the MOST FITTING emoji from the available list above.

Return ONLY a JSON array of arrays, where each inner array has exactly 3 elements:
- Index 0: The category name (exactly as it appears in the categories above)
- Index 1: The emoji name (exactly as it appears in the available list above)
- Index 2: The filter name (string)

Example format:
[
  ["Smileys", "Grinning%20Face", "networking"],
  ["Objects", "Graduation%20Cap", "career fair"],
  ["Objects", "Musical%20Note", "live music"],
  ["Objects", "Books", "workshop"]
]

NO explanations, NO additional text, JUST the JSON array.
"""

        try:
            logger.info(
                f"Generating recommended filters from {len(event_summaries)} events"
            )

            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates search keywords with emojis. Always return valid JSON arrays with the exact structure requested.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=15000,
            )

            response_text = response.choices[0].message.content.strip()

            # Remove markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            filters = json.loads(response_text.strip())

            if not isinstance(filters, list):
                logger.error("Response is not a list")
                return []

            # Clean and validate filters
            cleaned_filters = []
            for filter_item in filters:
                if (
                    isinstance(filter_item, list)
                    and len(filter_item) == 3
                    and isinstance(filter_item[0], str)
                    and isinstance(filter_item[1], str)
                    and isinstance(filter_item[2], str)
                    and filter_item[0].strip()
                    and filter_item[1].strip()
                    and filter_item[2].strip()
                ):
                    category = filter_item[0].strip()
                    emoji_string = filter_item[1].strip()
                    filter_name = filter_item[2].strip()

                    # Validate that the category exists and emoji exists in that category
                    if (
                        category in EMOJI_CATEGORIES
                        and emoji_string in EMOJI_CATEGORIES[category]
                    ):
                        cleaned_filters.append([category, emoji_string, filter_name])
                    else:
                        logger.warning(
                            f"Invalid filter emoji combination: category='{category}', emoji='{emoji_string}'"
                        )

            logger.info(
                f"Generated {len(cleaned_filters)} recommended filters with emojis"
            )
            return cleaned_filters[:15]

        except json.JSONDecodeError:
            logger.exception("Error parsing JSON response for filters")
            logger.error(f"Response text: {response_text}")
            return []
        except Exception:
            logger.exception("Error generating recommended filters")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def extract_event_links_from_website(self, raw_text: str, base_url: str | None = None) -> set[str]:
        """Send page text, return a JSON array of href strings"""
        if not raw_text:
            return set()

        def normalize(h: str) -> str:
            h = h.strip().strip('"\'')
            return urljoin(base_url, h) if base_url else h

        prompt = (
            "Return ONLY a JSON array of URL strings (absolute or relative) that correspond to individual "
            "event pages. Use the context (dates/times, event descriptions, LINK: ... -> href lines) to decide.\n\n"
            "Text (BEGIN):\n"
            f"{raw_text}\n"
            "Text (END)"
        )

        messages = [
            {"role": "system", "content": "You are a strict classifier: return ONLY a JSON array of href strings, no other text."},
            {"role": "user", "content": prompt},
        ]

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, temperature=0.0, max_tokens=1500
            )
        except Exception as e:
            logger.exception("OpenAI request failed: %s", e)
            return set()

        resp_text = ""
        try:
            resp_text = resp.choices[0].message.content.strip()
        except Exception:
            try:
                resp_text = str(resp.choices[0].text).strip()
            except Exception:
                resp_text = ""

        if not resp_text:
            logger.warning("Empty AI response when extracting event links")
            return set()

        data = None
        try:
            data = json.loads(resp_text)
        except Exception:
            m = re.search(r"(\[.*\])", resp_text, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(1))
                except Exception:
                    data = None

        if not isinstance(data, list):
            logger.debug("AI did not return a JSON array; raw response: %s", resp_text[:1000])
            return set()

        return {normalize(item) for item in data if isinstance(item, str)}
    


# Singleton instance
openai_service = OpenAIService()

# Backward compatibility - export functions that use the singleton
generate_embedding = openai_service.generate_embedding
extract_events_from_caption = openai_service.extract_events_from_caption
generate_recommended_filters = openai_service.generate_recommended_filters
generate_event_embedding = openai_service.generate_event_embedding
