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

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    text = text.replace("\n", " ").strip()
    if not text:
        return None

    response = client.embeddings.create(input=[text], model=model)

    return response.data[0].embedding


def extract_events_from_caption(
    caption_text: str, image_url: str | None = None
) -> list[dict[str, str | bool | float | None]]:
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
            "name": string,  // name of the event
            "date": string,  // date in YYYY-MM-DD format if found, empty string if not
            "start_time": string,  // start time in HH:MM format if found, empty string if not
            "end_time": string,  // end time in HH:MM format if found, empty string if not
            "location": string,  // location of the event
            "price": number or null,  // price in dollars (e.g., 15.00) if mentioned, null if free or not mentioned
            "food": string,  // food information if mentioned, empty string if not
            "registration": boolean,  // true if registration is required/mentioned, false otherwise
            "image_url": string,  // URL of the event image if provided, empty string if not
            "description": string  // the caption text word-for-word, followed by any additional insights from the image not in the caption
        }}
    ]
    
    Guidelines:
    - PRIORITIZE CAPTION TEXT: Always extract information from the caption text first and use it as the primary source of truth
    - Return an array of events - if multiple events are mentioned, create separate objects for each
    - If multiple dates are mentioned (e.g., "Friday and Saturday"), create separate events for each date
    - If recurring events are mentioned (e.g., "every Friday"), just create one event
    - For dates, use YYYY-MM-DD format. If year not found, assume 2025
    - For times, use HH:MM format (24-hour)
    - When interpreting relative terms like "tonight", "weekly", "every Friday", use the current date context above
    - For weekly events, calculate the next occurrence based on the current date and day of week
    - For price: extract dollar amounts (e.g., "$15", "15 dollars", "cost: $20") as numbers, use null for free events or when not mentioned
    - For food: extract and list only specific food or beverage items mentioned (e.g., "pizza", "cookies", "bubble tea", "snacks", "drinks")
    - For registration: only set to true if there is a clear instruction to register, RSVP, sign up, or follow a link before the event, otherwise they do not need registration so set to false
    - For description: start with the caption text word-for-word, then append any additional insights extracted from the image that are not already mentioned in the caption (e.g., visual details, atmosphere, decorations, crowd size, specific activities visible)
    - If information is not available, use empty string "" for strings, null for price, false for registration
    - Be consistent with the exact field names
    - Return ONLY the JSON array, no additional text
    - If no events are found, return an empty array []
    {f"- An image is provided at: {image_url}. If there are conflicts between caption and image information, ALWAYS prioritize the caption text over visual cues from the image." if image_url else ""}
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
        if image_url:
            logger.debug(f"Including image analysis from: {image_url}")
            messages[1]["content"].append(
                {"type": "image_url", "image_url": {"url": image_url}}
            )
            model = "gpt-4o-mini"  # Use vision-capable model
        else:
            model = "gpt-4o-mini"

        response = client.chat.completions.create(
            model=model, messages=messages, temperature=0.1, max_tokens=500
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
                    "name",
                    "date",
                    "start_time",
                    "end_time",
                    "location",
                    "price",
                    "food",
                    "registration",
                    "image_url",
                    "description",
                ]
                for field in required_fields:
                    if field not in event_data:
                        if field == "price":
                            event_data[field] = None
                        elif field == "registration":
                            event_data[field] = False
                        else:
                            event_data[field] = ""

                # Set image_url if provided
                if image_url and not event_data.get("image_url"):
                    event_data["image_url"] = image_url

                processed_events.append(event_data)

            return processed_events

        except json.JSONDecodeError:
            logger.exception("Error parsing JSON response")
            logger.error(f"Response text: {response_text}")
            # Return default structure if JSON parsing fails
            return [_get_default_event_structure(image_url)]

    except Exception:
        logger.exception("Error parsing caption")
        logger.error(f"Caption text: {caption_text}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return default structure if API call fails
        return [_get_default_event_structure(image_url)]


def _get_default_event_structure(
    image_url: str | None = None,
) -> dict[str, str | bool | float | None]:
    return {
        "name": "",
        "date": "",
        "start_time": "",
        "end_time": "",
        "location": "",
        "price": None,
        "food": "",
        "registration": False,
        "image_url": image_url if image_url else "",
        "description": "",
    }
