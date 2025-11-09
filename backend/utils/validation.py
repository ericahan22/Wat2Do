"""
Simple validation utility for event submissions.
"""
from typing import Dict, Any
from django.utils.html import strip_tags


def validate_event_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize event data. Returns cleaned data or raises ValueError.
    """
    if not isinstance(data, dict):
        raise ValueError("Event data must be a dictionary")
    
    # Required fields
    title = data.get("title", "").strip()
    location = data.get("location", "").strip()
    occurrences = data.get("occurrences", [])
    
    if not title or len(title) < 3:
        raise ValueError("Title is required and must be at least 3 characters")
    if not location or len(location) < 3:
        raise ValueError("Location is required and must be at least 3 characters")
    if not occurrences or not isinstance(occurrences, list) or len(occurrences) == 0:
        raise ValueError("At least one occurrence is required")
    
    # Validate occurrences
    cleaned_occurrences = []
    for occ in occurrences:
        if not isinstance(occ, dict):
            continue
        start_utc = occ.get("start_utc", "").strip()
        if not start_utc:
            continue
        cleaned_occ = {"start_utc": start_utc}
        if occ.get("end_utc"):
            cleaned_occ["end_utc"] = str(occ.get("end_utc")).strip()
        if occ.get("tz"):
            cleaned_occ["tz"] = str(occ.get("tz")).strip()
        cleaned_occurrences.append(cleaned_occ)
    
    if not cleaned_occurrences:
        raise ValueError("At least one occurrence with start_utc is required")
    
    # Sanitize text fields
    cleaned = {
        "title": strip_tags(title)[:500],
        "location": strip_tags(location)[:500],
        "occurrences": cleaned_occurrences,
    }
    
    # Optional fields
    if data.get("description"):
        cleaned["description"] = strip_tags(str(data.get("description")))[:5000]
    if data.get("food"):
        cleaned["food"] = strip_tags(str(data.get("food")))[:255]
    
    # Price
    price = data.get("price")
    if price is not None:
        try:
            price = float(price)
            if 0 <= price <= 10000:
                cleaned["price"] = price
        except (ValueError, TypeError):
            pass
    
    # Boolean
    if data.get("registration"):
        cleaned["registration"] = bool(data.get("registration"))
    
    return cleaned
