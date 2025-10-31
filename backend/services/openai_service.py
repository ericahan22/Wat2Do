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

from dotenv import load_dotenv
from openai import OpenAI

from scraping.logging_config import logger
from shared.constants.emojis import EMOJI_CATEGORIES


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
    ) -> dict[str, str | bool | float | None]:
        """Extract a SINGLE event from caption text/image. Multiple dates -> use rdate list."""
        # Get current date and day of week for context
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_day_of_week = now.strftime("%A")

        # Use post creation time if provided, otherwise use current time
        context_datetime = post_created_at if post_created_at else now
        context_date = context_datetime.strftime("%Y-%m-%d")
        context_day = context_datetime.strftime("%A")
        context_time = context_datetime.strftime("%H:%M")

        prompt = f"""
    Analyze the following Instagram caption and extract event information if it's an event post.

    School context: This post is from {school}. Use this to guide location and timezone decisions.
    Current context: Today is {current_day_of_week}, {current_date}
    Post was created on: {context_day}, {context_date} at {context_time}

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

    If you determine that there is NO event in the post, return the JSON value: null (not an object, not an array, just the literal null). Otherwise, return ONE JSON object (not an array) with ALL of the following fields:
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
        "rdate": array,               // additional occurrence dates as ["YYYY-MM-DD", ...] when multiple dates are listed
        "school": string,
        "source_image_url": string,
        "description": string
    }}

    IMPORTANT RULES:
    - Return EXACTLY ONE JSON object. NEVER return an array.
    - If multiple dates are listed (e.g., "Friday and Saturday" or explicit multiple dates), keep the primary occurrence in dtstart/dtend and put the additional occurrence dates (dates only) into rdate as an array of ISO dates.
    - PRIORITIZE CAPTION TEXT for extracting fields. Only prefer image text for the title when the caption lacks a clear title.
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
    - For rrule: only when recurring is mentioned; otherwise empty string.
    - For description: start with the caption text word-for-word, then append any additional insights about the event extracted from the image that are not already mentioned in the caption.
    - If the content violates the STRICT CONTENT POLICY or is not an event, set title to "" and leave the rest of the fields empty as per defaults below. Do not fabricate an event.
    - If information is not available, use empty string for strings, null for price/coordinates, and false for booleans.
    - Return ONLY the JSON object text, no extra commentary.
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
                model = "gpt-4o-mini"  # Use vision-capable model
            else:
                model = "gpt-4o-mini"

            # If image download by OpenAI errors out, retry without image content by using URL in text
            try:
                response = self.client.chat.completions.create(
                    model=model, messages=messages, temperature=0.1, max_tokens=2000
                )
            except Exception as e:
                err_text = str(e)
                if (
                    "invalid_image_url" in err_text
                    or "Timeout while downloading" in err_text
                ):
                    logger.warning(
                        f"OpenAI failed to fetch the image ({err_text}); retrying without image"
                    )
                    fallback = deepcopy(messages)
                    if isinstance(fallback[1].get("content"), list):
                        fallback[1]["content"] = [
                            c
                            for c in fallback[1]["content"]
                            if not (
                                isinstance(c, dict) and c.get("type") == "image_url"
                            )
                        ]
                        if source_image_url:
                            if (
                                isinstance(fallback[1]["content"][0], dict)
                                and "text" in fallback[1]["content"][0]
                            ):
                                fallback[1]["content"][0]["text"] += (
                                    f"\n\nImage URL: {source_image_url}"
                                )
                            else:
                                fallback[1]["content"].insert(
                                    0,
                                    {
                                        "type": "text",
                                        "text": f"Image URL: {source_image_url}",
                                    },
                                )
                    time.sleep(1)
                    try:
                        response = self.client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=fallback,
                            temperature=0.1,
                            max_tokens=2000,
                        )
                    except Exception as e:
                        logger.exception(
                            f"Retry without image also failed, returning default structure: {e}"
                        )
                        return _get_default_event_structure(source_image_url)

            # Extract the JSON response
            response_text = response.choices[0].message.content.strip()

            # Try to parse the JSON response
            try:
                # Remove any markdown formatting if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]

                event_data = json.loads(response_text.strip())

                # If the model returned an array, take the first element for backward compatibility
                if isinstance(event_data, list):
                    event_data = event_data[0] if event_data else {}

                if not isinstance(event_data, dict):
                    logger.warning("Response is not an object, returning None (no event)")
                    return None

                # Ensure required fields are present
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
                for field in required_fields:
                    if field not in event_data:
                        if field in ["price", "latitude", "longitude"]:
                            event_data[field] = None
                        elif field in ["registration", "all_day"]:
                            event_data[field] = False
                        elif field == "rdate":
                            event_data[field] = []
                        else:
                            event_data[field] = ""

                # Set source_image_url if provided
                if source_image_url and not event_data.get("source_image_url"):
                    event_data["source_image_url"] = source_image_url

                return event_data

            except json.JSONDecodeError:
                logger.exception("Error parsing JSON response")
                logger.error(f"Response text: {response_text}")
                # Return default structure if JSON parsing fails
                return _get_default_event_structure(source_image_url)

        except Exception:
            logger.exception("Error parsing caption")
            logger.error(f"Caption text: {caption_text}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Return default structure if API call fails
            return _get_default_event_structure(source_image_url)

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
                model="gpt-4o-mini",
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


def _get_default_event_structure(
    source_image_url: str | None = None,
) -> dict[str, str | bool | float | None]:
    """Helper function to create default event structure"""
    return {
        "title": "",
        "dtstart": "",
        "dtend": "",
        "dtstart_utc": "",
        "dtend_utc": "",
        "all_day": False,
        "location": "",
        "latitude": None,
        "longitude": None,
        "tz": "America/Toronto",
        "price": None,
        "food": "",
        "registration": False,
        "rrule": "",
        "rdate": [],
        "school": "University of Waterloo",
        "source_image_url": source_image_url or "",
        "description": "",
    }


# Singleton instance
openai_service = OpenAIService()

# Backward compatibility - export functions that use the singleton
generate_embedding = openai_service.generate_embedding
extract_events_from_caption = openai_service.extract_events_from_caption
generate_recommended_filters = openai_service.generate_recommended_filters
generate_event_embedding = openai_service.generate_event_embedding
