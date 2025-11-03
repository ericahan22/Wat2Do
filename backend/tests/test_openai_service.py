import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.openai_service import extract_events_from_caption


image_url = "https://bug-free-octo-spork.s3.us-east-2.amazonaws.com/events/daf5bcdd-ee6b-4bbd-9ef1-e0f4b2b8f397.jpg"
post_caption=""

# Test AI client
result = extract_events_from_caption(post_caption, image_url)
print(result)
