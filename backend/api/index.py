"""
Vercel API entry point for Django application.
This file is used by Vercel to serve the Django API.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Import Django and get the WSGI application
from django.core.wsgi import get_wsgi_application

# Vercel expects this variable
app = get_wsgi_application()

# Alternative variable name
handler = app
