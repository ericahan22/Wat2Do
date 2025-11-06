"""
Utility functions for processing event submissions.
Automatically computes derived fields from user-provided basic event data.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import pytz
from dateutil import parser as dateutil_parser
from django.utils import timezone
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Common University of Waterloo locations with their coordinates
UW_LOCATION_LOOKUP = {
    # Buildings
    "dc": (43.4729, -80.5419),  # Davis Centre
    "davis centre": (43.4729, -80.5419),
    "davis center": (43.4729, -80.5419),
    "mc": (43.4715, -80.5437),  # Mathematics & Computer Building
    "math building": (43.4715, -80.5437),
    "slc": (43.4718, -80.5459),  # Student Life Centre
    "student life centre": (43.4718, -80.5459),
    "student life center": (43.4718, -80.5459),
    "pac": (43.4728, -80.5462),  # Physical Activities Complex
    "cif": (43.4738, -80.5481),  # Columbia Icefield
    "e7": (43.4723, -80.5407),  # Engineering 7
    "e5": (43.4709, -80.5400),  # Engineering 5
    "qnc": (43.4711, -80.5444),  # Quantum Nano Centre
    "sch": (43.4694, -80.5422),  # South Campus Hall
    "dc library": (43.4729, -80.5419),
    "dana porter": (43.4693, -80.5422),
    "dp": (43.4693, -80.5422),
    "dana porter library": (43.4693, -80.5422),
    "hagey hall": (43.4688, -80.5419),
    "hh": (43.4688, -80.5419),
    # General campus
    "university of waterloo": (43.4723, -80.5449),
    "uw": (43.4723, -80.5449),
    "waterloo campus": (43.4723, -80.5449),
}

# Default timezone for University of Waterloo
DEFAULT_TIMEZONE = "America/Toronto"

# Initialize geocoder (with a user agent as required by Nominatim)
geolocator = Nominatim(user_agent="wat2do-event-submission", timeout=5)


def parse_datetime_string(dt_str: str, tz_str: str = None) -> Optional[datetime]:
    """
    Parse a datetime string into a timezone-aware datetime object.
    
    Args:
        dt_str: DateTime string in various formats
        tz_str: Timezone string (e.g., "America/Toronto")
        
    Returns:
        Timezone-aware datetime object or None if parsing fails
    """
    if not dt_str:
        return None
        
    try:
        # Try parsing the string
        dt = dateutil_parser.parse(dt_str)
        
        # Make timezone-aware if naive
        if timezone.is_naive(dt):
            tz = pytz.timezone(tz_str) if tz_str else pytz.timezone(DEFAULT_TIMEZONE)
            dt = timezone.make_aware(dt, tz)
            
        return dt
    except Exception:
        return None


def geocode_location(location: str, school: str = "University of Waterloo") -> Tuple[Optional[float], Optional[float]]:
    """
    Geocode a location string to latitude/longitude coordinates.
    
    First checks common UW location lookup table, then falls back to geocoding service.
    
    Args:
        location: Location description (e.g., "DC Library", "200 University Ave W")
        school: School name for context
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if geocoding fails
    """
    if not location:
        return None, None
    
    # Normalize location string for lookup
    location_normalized = location.lower().strip()
    
    # Check common UW locations first
    if location_normalized in UW_LOCATION_LOOKUP:
        return UW_LOCATION_LOOKUP[location_normalized]
    
    # Check if any key is contained in the location string
    for key, coords in UW_LOCATION_LOOKUP.items():
        if key in location_normalized:
            return coords
    
    # Fall back to geocoding service
    try:
        # Add school context if not already present
        query = location
        if school and school.lower() not in location.lower():
            query = f"{location}, {school}"
        
        # Try geocoding
        result = geolocator.geocode(query)
        if result:
            return result.latitude, result.longitude
    except (GeocoderTimedOut, GeocoderServiceError):
        # Geocoding failed, return None
        pass
    except Exception:
        # Any other error, return None
        pass
    
    return None, None


def compute_event_fields(event_data: Dict[str, Any], screenshot_url: str = None) -> Dict[str, Any]:
    """
    Compute derived fields for an event submission.
    
    Takes basic event data provided by user and computes:
    - dtstart_utc: UTC version of dtstart
    - dtend_utc: UTC version of dtend
    - duration: Duration between dtstart and dtend
    - tz: Timezone (defaults to America/Toronto for UW)
    - latitude/longitude: Geocoded from location
    - source_image_url: Set from screenshot_url
    
    Args:
        event_data: Dictionary with basic event fields (title, dtstart, dtend, location, etc.)
        screenshot_url: URL of the uploaded screenshot
        
    Returns:
        Updated event_data dictionary with computed fields
    """
    # Make a copy to avoid mutating the input
    computed_data = event_data.copy()
    
    # 1. Set timezone (default to Toronto for UW)
    if "tz" not in computed_data or not computed_data.get("tz"):
        computed_data["tz"] = DEFAULT_TIMEZONE
    
    tz_str = computed_data["tz"]
    
    # 2. Parse dtstart and compute dtstart_utc
    dtstart_str = computed_data.get("dtstart")
    if dtstart_str:
        dtstart = parse_datetime_string(dtstart_str, tz_str)
        if dtstart:
            # Store the local time version
            if isinstance(dtstart_str, str):
                computed_data["dtstart"] = dtstart
            
            # Compute UTC version
            computed_data["dtstart_utc"] = dtstart.astimezone(pytz.UTC)
    
    # 3. Parse dtend and compute dtend_utc
    dtend_str = computed_data.get("dtend")
    dtstart = computed_data.get("dtstart")
    if dtend_str:
        dtend = parse_datetime_string(dtend_str, tz_str)
        if dtend:
            # Store the local time version
            if isinstance(dtend_str, str):
                computed_data["dtend"] = dtend
            
            # Compute UTC version
            computed_data["dtend_utc"] = dtend.astimezone(pytz.UTC)
            
            # 4. Compute duration if both dtstart and dtend exist
            if dtstart and isinstance(dtstart, datetime):
                computed_data["duration"] = dtend - dtstart
    
    # 5. Geocode location to get latitude/longitude
    location = computed_data.get("location")
    school = computed_data.get("school", "University of Waterloo")
    
    if location and ("latitude" not in computed_data or "longitude" not in computed_data):
        latitude, longitude = geocode_location(location, school)
        if latitude is not None and longitude is not None:
            computed_data["latitude"] = latitude
            computed_data["longitude"] = longitude
    
    # 6. Set source_image_url from screenshot_url
    if screenshot_url and "source_image_url" not in computed_data:
        computed_data["source_image_url"] = screenshot_url
    
    return computed_data

