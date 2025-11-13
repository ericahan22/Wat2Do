import os

from .base import *

# Production settings
DEBUG = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HTTPS Security Headers
SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)  # For proxies like Vercel/ELB

# Session security
SESSION_COOKIE_SECURE = True  # Only send session cookies over HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# CSRF security
CSRF_COOKIE_SECURE = True  # Only send CSRF cookies over HTTPS
CSRF_COOKIE_HTTPONLY = False  # Keep False for SPA compatibility, but ensure proper CORS
CSRF_COOKIE_SAMESITE = "Lax"

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
