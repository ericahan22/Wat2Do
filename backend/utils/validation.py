"""
Input validation and sanitization utilities for event submissions.
"""
import re
from typing import Dict, Any, Optional
from django.utils.html import escape, strip_tags


# Maximum length constraints for user-submitted fields
MAX_LENGTHS = {
    'title': 500,
    'description': 5000,
    'location': 500,
    'food': 255,
    'school': 255,
    'club_type': 50,
    'ig_handle': 100,
    'discord_handle': 100,
    'x_handle': 100,
    'tiktok_handle': 100,
    'fb_handle': 100,
    'other_handle': 100,
}

# Fields that users are allowed to submit/edit
USER_EDITABLE_FIELDS = {
    'title',
    'description',
    'location',
    'dtstart',
    'dtend',
    'food',
    'registration',
    'price',
    'school',
    'club_type',
    'ig_handle',
    'discord_handle',
    'x_handle',
    'tiktok_handle',
    'fb_handle',
    'other_handle',
    'all_day',
    'categories',
}

# Fields that admins can edit (includes user editable fields plus some admin-only fields)
ADMIN_EDITABLE_FIELDS = USER_EDITABLE_FIELDS | {
    'status',
    'source_url',
    'source_image_url',
    'rrule',
    'rdate',
}

# Protected fields that should never be directly set by users or admins through API
PROTECTED_FIELDS = {
    'id',
    'added_at',
    'dtstamp',
    'dtstart_utc',  # Computed from dtstart
    'dtend_utc',    # Computed from dtend
    'duration',     # Computed from dtstart/dtend
    'latitude',     # Computed from location
    'longitude',    # Computed from location
    'tz',          # Computed/defaulted
    'raw_json',    # System field
    'reactions',   # System field
}


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text input by stripping HTML tags and trimming whitespace.
    
    Args:
        text: Input text to sanitize
        max_length: Optional maximum length to enforce
        
    Returns:
        Sanitized text string
    """
    if not isinstance(text, str):
        return ""
    
    # Strip HTML tags to prevent XSS
    sanitized = strip_tags(text)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Enforce max length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def sanitize_url(url: str) -> str:
    """
    Basic URL sanitization.
    
    Args:
        url: URL string to sanitize
        
    Returns:
        Sanitized URL
    """
    if not isinstance(url, str):
        return ""
    
    url = url.strip()
    
    # Basic validation - must start with http:// or https://
    if url and not url.startswith(('http://', 'https://')):
        return ""
    
    return url


def sanitize_social_handle(handle: str) -> str:
    """
    Sanitize social media handle by removing @ symbols and special characters.
    
    Args:
        handle: Social media handle
        
    Returns:
        Sanitized handle
    """
    if not isinstance(handle, str):
        return ""
    
    # Remove @ symbol if present
    handle = handle.lstrip('@')
    
    # Remove any HTML tags
    handle = strip_tags(handle)
    
    # Only allow alphanumeric, underscore, hyphen, and period
    handle = re.sub(r'[^\w\-\.]', '', handle)
    
    return handle.strip()


def validate_and_sanitize_event_data(
    data: Dict[str, Any],
    allowed_fields: set = None,
    is_admin: bool = False
) -> Dict[str, Any]:
    """
    Validate and sanitize event submission data.
    
    Args:
        data: Raw event data from user
        allowed_fields: Set of fields that are allowed to be set (defaults to USER_EDITABLE_FIELDS or ADMIN_EDITABLE_FIELDS)
        is_admin: Whether the user is an admin (allows additional fields)
        
    Returns:
        Cleaned and validated event data dictionary
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(data, dict):
        raise ValueError("Event data must be a dictionary")
    
    # Use admin fields if admin, otherwise use user fields
    if allowed_fields is None:
        if is_admin:
            allowed_fields = ADMIN_EDITABLE_FIELDS
        else:
            allowed_fields = USER_EDITABLE_FIELDS
    
    cleaned_data = {}
    
    for field, value in data.items():
        # Skip protected fields
        if field in PROTECTED_FIELDS:
            continue
        
        # Skip fields not in allowed list
        if field not in allowed_fields:
            continue
        
        # Skip empty values
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        
        # Handle text fields
        if field in {'title', 'description', 'location', 'food', 'school', 'club_type'}:
            max_len = MAX_LENGTHS.get(field)
            cleaned_value = sanitize_text(value, max_len)
            if cleaned_value:
                cleaned_data[field] = cleaned_value
        
        # Handle social media handles
        elif field in {'ig_handle', 'discord_handle', 'x_handle', 'tiktok_handle', 'fb_handle', 'other_handle'}:
            max_len = MAX_LENGTHS.get(field, 100)
            cleaned_value = sanitize_social_handle(value)
            if cleaned_value and len(cleaned_value) <= max_len:
                cleaned_data[field] = cleaned_value
        
        # Handle URLs
        elif field in {'source_url', 'source_image_url'}:
            cleaned_value = sanitize_url(value)
            if cleaned_value:
                cleaned_data[field] = cleaned_value
        
        # Handle boolean fields
        elif field in {'registration', 'all_day'}:
            if isinstance(value, bool):
                cleaned_data[field] = value
            elif isinstance(value, str):
                cleaned_data[field] = value.lower() in ('true', '1', 'yes')
        
        # Handle numeric fields
        elif field == 'price':
            try:
                price = float(value)
                if 0 <= price <= 10000:  # Reasonable max price
                    cleaned_data[field] = price
            except (ValueError, TypeError):
                pass
        
        # Handle datetime fields - pass through for now, will be validated by compute_event_fields
        elif field in {'dtstart', 'dtend'}:
            if isinstance(value, str) and value.strip():
                cleaned_data[field] = value.strip()
        
        # Handle status field (admin only)
        elif field == 'status' and is_admin:
            if isinstance(value, str) and value.upper() in {'CONFIRMED', 'TENTATIVE', 'CANCELLED', 'PENDING'}:
                cleaned_data[field] = value.upper()
        
        # Handle categories (list field)
        elif field == 'categories':
            if isinstance(value, list):
                # Sanitize each category
                sanitized_cats = [
                    sanitize_text(cat, 50) 
                    for cat in value 
                    if isinstance(cat, str)
                ]
                if sanitized_cats:
                    cleaned_data[field] = sanitized_cats
        
        # Handle rrule and rdate (admin only)
        elif field in {'rrule', 'rdate'} and is_admin:
            cleaned_data[field] = value
    
    return cleaned_data


def validate_required_fields(data: Dict[str, Any]) -> None:
    """
    Validate that required fields are present.
    
    Args:
        data: Event data to validate
        
    Raises:
        ValueError: If required fields are missing
    """
    if not data.get('title'):
        raise ValueError("Title is required")
    
    if not data.get('dtstart'):
        raise ValueError("Start date/time is required")
    
    if not data.get('location'):
        raise ValueError("Location is required")
    
    # Validate title length
    if len(data['title']) < 3:
        raise ValueError("Title must be at least 3 characters long")
    
    # Validate location length
    if len(data.get('location', '')) < 3:
        raise ValueError("Location must be at least 3 characters long")




