"""
Minimal Vercel API entry point to test Django compatibility.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Simple test function
def handler(request):
    """
    Simple test handler to see if Django can load.
    """
    try:
        # Try to import Django
        import django
        django.setup()
        
        # Try to import a simple Django component
        from django.http import HttpResponse
        
        return HttpResponse("Django loaded successfully!", content_type="text/plain")
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error loading Django: {str(e)}",
            "headers": {"Content-Type": "text/plain"}
        }

# Vercel expects these variables
app = handler
