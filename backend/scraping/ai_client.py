import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import logging
import traceback
from datetime import datetime


logger = logging.getLogger(__name__)


# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_caption_for_event(caption_text, image_url=None):
    """
    Parse an Instagram caption to extract event information.
    Returns a consistent JSON format with all required fields.
    
    Args:
        caption_text (str or None): Instagram caption text (can be None)
        image_url (str, optional): URL to image for enhanced analysis
    """
    
    # Get current date and day of week for context
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_day_of_week = now.strftime("%A")
    
    prompt = f"""
    Analyze the following Instagram caption and extract event information if it's an event post.
    
    Current context: Today is {current_day_of_week}, {current_date}
    
    Caption: {caption_text}
    
    Return a JSON object with the following structure (all fields must be present):
    {{
        "name": string,  // name of the event
        "date": string,  // date in YYYY-MM-DD format if found, empty string if not
        "start_time": string,  // start time in HH:MM format if found, empty string if not
        "end_time": string,  // end time in HH:MM format if found, empty string if not
        "location": string,,  // location of the event
        "price": number or null,  // price in dollars (e.g., 15.00) if mentioned, null if free or not mentioned
        "food": string,  // food information if mentioned, empty string if not
        "registration": boolean  // true if registration is required/mentioned, false otherwise
        "image_url": string  // URL of the event image if provided, empty string if not
    }}
    
    Guidelines:
    - For dates, use YYYY-MM-DD format. If year not found, assume 2025
    - For times, use HH:MM format (24-hour)
    - When interpreting relative terms like "tonight", "weekly", "every Friday", use the current date context above
    - For weekly events, calculate the next occurrence based on the current date and day of week
    - For price: extract dollar amounts (e.g., "$15", "15 dollars", "cost: $20") as numbers, use null for free events or when not mentioned
    - For food: extract and list only specific food or beverage items mentioned (e.g., "pizza", "cookies", "bubble tea", "snacks", "drinks")
    - For registration: only set to true if there is a clear instruction to register, RSVP, sign up, or follow a link before the event, otherwise they do not need registration so set to false
    - If information is not available, use empty string "" for strings, null for price, false for registration
    - Be consistent with the exact field names
    - Return ONLY the JSON object, no additional text
    {f"- An image is provided at: {image_url}. Use visual cues from the image to enhance event extraction." if image_url else ""}
    """
    
    try:
        logger.debug(f"Parsing caption of length: {len(caption_text)}")
        logger.debug(f"Caption preview: {caption_text[:100]}...")
        
        # Prepare messages for the API call
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts event information from social media posts. Always return valid JSON with the exact structure requested."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        # Add image to the message if provided
        if image_url:
            logger.debug(f"Including image analysis from: {image_url}")
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
            model = "gpt-4o-mini"  # Use vision-capable model
        else:
            model = "gpt-4o-mini"
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,
            max_tokens=500
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
            
            event_data = json.loads(response_text.strip())
            
            # Ensure all required fields are present
            required_fields = ["name", "date", "start_time", "end_time", "location", 
                             "price", "food", "registration", "image_url"]
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
            
            return event_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response text: {response_text}")
            # Return default structure if JSON parsing fails
            return {
                "name": "",
                "date": "",
                "start_time": "",
                "end_time": "",
                "location": "",
                "price": None,
                "food": "",
                "registration": False,
                "image_url": image_url if image_url else ""
            }
            
    except Exception as e:
        logger.error(f"Error parsing caption: {str(e)}")
        logger.error(f"Caption text: {caption_text}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return default structure if API call fails
        return {
            "name": "",
            "date": "",
            "start_time": "",
            "end_time": "",
            "location": "",
            "price": None,
            "food": "",
            "registration": False,
            "image_url": image_url if image_url else ""
        } 