"""
OpenAI service for AI-powered text analysis and embeddings.

This module provides methods for interacting with OpenAI's API, including:
- Text embeddings generation
- Event information extraction from social media captions
- Image analysis for event data
"""

import json
import logging
import os
import traceback
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector for text using OpenAI's text-embedding-3-small model (1536 dimensions).
        """
        if not text:
            return None

        # Clean up the text for better embedding quality
        text = text.replace("\n", " ").replace("\r", " ").strip()

        # Remove extra whitespace
        import re

        text = re.sub(r"\s+", " ", text)

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
        self, caption_text: str, source_image_url: str | None = None
    ) -> list[dict[str, str | bool | float | None]]:
        """Extract event information from Instagram caption text and optional image"""
        # Get current date and day of week for context
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_day_of_week = now.strftime("%A")

        prompt = f"""
    Analyze the following Instagram caption and extract event information if it's an event post.
    
    Current context: Today is {current_day_of_week}, {current_date}
    
    Caption: {caption_text}
    
    Return a JSON array of event objects. Each event should have the following structure (all fields must be present):
    [
        {{
            "title": string,  // name of the event
            "dtstart": string,  // start date in YYYY-MM-DD HH:MM:SS±HH format if found, empty string if not
            "dtend": string,  // end date in YYYY-MM-DD HH:MM:SS±HH format if found, empty string if not
            "location": string,  // location of the event
            "price": number or null,  // price in dollars (e.g., 15.00) if mentioned, null if free or not mentioned
            "food": string,  // food information if mentioned, empty string if not
            "registration": boolean,  // true if registration is required/mentioned, false otherwise
            "source_image_url": string,  // URL of the event image if provided, empty string if not
            "description": string  // the caption text word-for-word, followed by any additional insights from the image not in the caption
        }}
    ]
    
    Guidelines:
    - PRIORITIZE CAPTION TEXT for extracting fields (dtstart, dtend, location, price, food, registration, description, etc.).
    - EXCEPTION: For the event "title" field ONLY, prefer an explicit title found in the image (e.g., poster text) if the caption does not contain a clear, explicit event title. If both caption and image provide a name, prefer the image-derived title for the "title" field; otherwise use the caption.
    - Return an array of events - if multiple events are mentioned, create separate objects for each
    - Title-case event titles (e.g., "...talk" -> "...Talk", "COFFEE CRAWL" -> "Coffee Crawl")
    - If multiple dates are mentioned (e.g., "Friday and Saturday"), create separate events for each date
    - If recurring events are mentioned (e.g., "every Friday"), just create one event
    - For dtstart and dtend, if year not found, assume 2025
    - When interpreting relative terms like "tonight", "tomorrow", "weekly", "every Friday", use the current date context above and the date the post was made. If an explicit date is found in the image, use that date
    - For weekly events, calculate the next occurrence based on the current date and day of week
    - For (off-campus) addresses: use the format "[Street Address], [City], [Province] [Postal Code]" when possible
    - For price: this represents REGISTRATION COST ONLY. Extract dollar amounts (e.g., "$15", "15 dollars", "cost: $20") as numbers, use null for free events or when not mentioned
    - For food: extract and list all specific food or beverage items mentioned, separated by commas (e.g., "Snacks, drinks", "Pizza, bubble tea"). Always capitalize the first item mentioned
    - If the exact food items are not mentioned, e.g., the literal word "food" would be returned, output "Yes!" (exactly) for the food field to indicate that food is present. Do not output the literal word "food" by itself.
    - For registration: only set to true if there is a clear instruction to register, RSVP, sign up, or follow a link before the event, otherwise they do not need registration so set to false
    - For description: start with the caption text word-for-word, then append any additional insights extracted from the image that are not already mentioned in the caption (e.g., visual details, atmosphere, decorations, crowd size, specific activities visible)
    - If information is not available, use empty string "" for strings, null for price, false for registration
    - Be consistent with the exact field names
    - Return ONLY the JSON array, no additional text
    - If no events are found, return an empty array []
        {f"- An image is provided at: {source_image_url}. If there are conflicts between caption and image information, ALWAYS prioritize the caption text over visual cues from the image." if source_image_url else ""}
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

            response = self.client.chat.completions.create(
                model=model, messages=messages, temperature=0.1, max_tokens=2000
            )

            # Extract the JSON response
            response_text = response.choices[0].message.content.strip()

            # Try to parse the JSON response
            try:
                # Remove any markdown formatting if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]

                events_data = json.loads(response_text.strip())

                # Ensure events_data is a list
                if not isinstance(events_data, list):
                    logger.warning("Response is not a list, wrapping in array")
                    events_data = [events_data] if events_data else []

                # Process each event in the array
                processed_events = []
                for event_data in events_data:
                    # Ensure all required fields are present
                    required_fields = [
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
                    for field in required_fields:
                        if field not in event_data:
                            if field == "price":
                                event_data[field] = None
                            elif field == "registration":
                                event_data[field] = False
                            else:
                                event_data[field] = ""

                    # Set source_image_url if provided
                    if source_image_url and not event_data.get("source_image_url"):
                        event_data["source_image_url"] = source_image_url

                    processed_events.append(event_data)

                return processed_events

            except json.JSONDecodeError:
                logger.exception("Error parsing JSON response")
                logger.error(f"Response text: {response_text}")
                # Return default structure if JSON parsing fails
                return [_get_default_event_structure(source_image_url)]

        except Exception:
            logger.exception("Error parsing caption")
            logger.error(f"Caption text: {caption_text}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Return default structure if API call fails
            return [_get_default_event_structure(source_image_url)]

    def generate_recommended_filters(self, events_data: list[dict]) -> list[str]:
        """Generate recommended filter keywords from upcoming events data using GPT"""
        if not events_data:
            logger.warning("No events data provided for filter generation")
            return []

        # Prepare event summaries for the prompt
        event_summaries = []
        for event in events_data[:200]:  # Limit to 200 events to avoid token limits
            summary = f"- {event.get('title', 'Unnamed')} at {event.get('location', 'TBD')}"
            if event.get("food"):
                summary += f" (food: {event.get('food')})"
            if event.get("club_type"):
                summary += f" [type: {event.get('club_type')}]"
            event_summaries.append(summary)

        prompt = f"""
Analyze the following list of {len(event_summaries)} upcoming student events and generate 20-25 search filter keywords.

Events:
{chr(10).join(event_summaries)}

Generate filter keywords that:
1. Capture the most common themes students care about (networking, meeting people, large events, food, professional development, etc.)
2. Are SHORT (1-3 words max) and SPECIFIC
3. Reflect actual patterns in the event data above
4. Focus on: event types, activities, professional topics, food/drinks, social aspects, clubs/organizations
5. Are diverse enough to cover different student interests

Return ONLY a JSON array of 20-25 keyword strings, like:
["networking", "free food", "career fair", "live music", "workshop", ...]

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
                        "content": "You are a helpful assistant that generates search keywords. Always return valid JSON arrays.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=300,
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
            cleaned_filters = [
                str(f).strip()
                for f in filters
                if f and isinstance(f, str) and len(str(f).strip()) > 0
            ]

            logger.info(f"Generated {len(cleaned_filters)} recommended filters")
            return list(set(cleaned_filters))[:25]

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
        "location": "",
        "price": None,
        "food": "",
        "registration": False,
        "source_image_url": source_image_url if source_image_url else "",
        "description": "",
    }


# Singleton instance
openai_service = OpenAIService()

# Backward compatibility - export functions that use the singleton
generate_embedding = openai_service.generate_embedding
extract_events_from_caption = openai_service.extract_events_from_caption
generate_recommended_filters = openai_service.generate_recommended_filters
