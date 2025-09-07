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

def parse_caption_for_event(caption_text):
    """
    Parse an Instagram caption to extract event information.
    Returns a consistent JSON format with all required fields.
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
        "location": string  // location of the event
    }}
    
    Guidelines:
    - For dates, use YYYY-MM-DD format. If year not found, assume 2025
    - For times, use HH:MM format (24-hour)
    - When interpreting relative terms like "tonight", "weekly", "every Friday", use the current date context above
    - For weekly events, calculate the next occurrence based on the current date and day of week
    - If information is not available, use empty string ""
    - Be consistent with the exact field names
    - Return ONLY the JSON object, no additional text
    """
    
    try:
        logger.debug(f"Parsing caption of length: {len(caption_text)}")
        logger.debug(f"Caption preview: {caption_text[:100]}...")
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions="You are a helpful assistant that extracts event information from social media posts. Always return valid JSON with the exact structure requested.",
            input=prompt,
            temperature=0.1
        )
        
        # Extract the JSON response
        response_text = response.output_text.strip()
        
        # Try to parse the JSON response
        try:
            # Remove any markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            event_data = json.loads(response_text.strip())
            
            # Ensure all required fields are present
            required_fields = ["name", "date", 
                             "start_time", "end_time", "location"]
            for field in required_fields:
                if field not in event_data:
                    event_data[field] = ""
            
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
                "location": ""
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
            "location": ""
        } 