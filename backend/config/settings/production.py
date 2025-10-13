import os

from .base import *

# Production settings
DEBUG = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

ALLOWED_HOSTS = [
    "api.wat2do.ca",
    "wat2do.ca",
    "www.wat2do.ca",
    ".elasticbeanstalk.com",
    ".elb.amazonaws.com",
    "3.147.72.188",
    "67.70.1.226",
    "10.0.0.4",
    "10.0.0.22",
]

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
