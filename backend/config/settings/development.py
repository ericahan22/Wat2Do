import os

from .base import *

# Development settings
DEBUG = True

# Development-specific apps
# INSTALLED_APPS += [
#     'django_extensions',
# ]

# Use SQLite if USE_SQLITE=1 is set
if os.getenv("USE_SQLITE") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
