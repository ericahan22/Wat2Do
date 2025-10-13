from .base import (
    BASE_DIR,
)

# Production settings
DEBUG = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Production-specific settings
ALLOWED_HOSTS = ["your-domain.com", "www.your-domain.com"]

# Static files
STATIC_ROOT = BASE_DIR / "staticfiles"
