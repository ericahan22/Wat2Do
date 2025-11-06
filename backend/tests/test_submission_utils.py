"""
Tests for submission utility functions.
"""

import pytest
from datetime import datetime, timedelta
import pytz
from utils.submission_utils import (
    parse_datetime_string,
    geocode_location,
    compute_event_fields,
)


class TestParseDatetimeString:
    """Test datetime string parsing."""
    
    def test_parse_iso_format(self):
        """Test parsing ISO format datetime."""
        result = parse_datetime_string("2025-11-05 17:00:00", "America/Toronto")
        assert result is not None
        assert result.year == 2025
        assert result.month == 11
        assert result.day == 5
        assert result.hour == 17
        assert result.tzinfo is not None
    
    def test_parse_with_timezone(self):
        """Test parsing datetime with timezone."""
        result = parse_datetime_string("2025-11-05 17:00:00-05:00")
        assert result is not None
        assert result.tzinfo is not None
    
    def test_parse_invalid_datetime(self):
        """Test parsing invalid datetime returns None."""
        result = parse_datetime_string("not a date")
        assert result is None


class TestGeocodeLocation:
    """Test location geocoding."""
    
    def test_geocode_dc_library(self):
        """Test geocoding DC Library (common UW location)."""
        lat, lon = geocode_location("DC Library")
        assert lat is not None
        assert lon is not None
        assert abs(lat - 43.4729) < 0.01  # Close to expected coordinates
        assert abs(lon - (-80.5419)) < 0.01
    
    def test_geocode_slc(self):
        """Test geocoding SLC (Student Life Centre)."""
        lat, lon = geocode_location("SLC")
        assert lat is not None
        assert lon is not None
        assert abs(lat - 43.4718) < 0.01
        assert abs(lon - (-80.5459)) < 0.01
    
    def test_geocode_invalid_location(self):
        """Test geocoding invalid location returns None."""
        lat, lon = geocode_location("")
        assert lat is None
        assert lon is None


class TestComputeEventFields:
    """Test event field computation."""
    
    def test_compute_basic_event(self):
        """Test computing fields for a basic event."""
        event_data = {
            "title": "Test Event",
            "dtstart": "2025-11-05 17:00:00",
            "dtend": "2025-11-05 19:00:00",
            "location": "DC Library",
        }
        screenshot_url = "https://example.com/screenshot.jpg"
        
        result = compute_event_fields(event_data, screenshot_url)
        
        # Check required fields are present
        assert result["title"] == "Test Event"
        assert result["dtstart"] is not None
        assert result["dtend"] is not None
        
        # Check computed fields
        assert result["dtstart_utc"] is not None
        assert result["dtend_utc"] is not None
        assert result["duration"] is not None
        assert result["tz"] == "America/Toronto"
        assert result["latitude"] is not None
        assert result["longitude"] is not None
        assert result["source_image_url"] == screenshot_url
    
    def test_compute_event_without_end_time(self):
        """Test computing fields for event without end time."""
        event_data = {
            "title": "Test Event",
            "dtstart": "2025-11-05 17:00:00",
            "location": "SLC",
        }
        
        result = compute_event_fields(event_data)
        
        # Check required fields
        assert result["title"] == "Test Event"
        assert result["dtstart"] is not None
        assert result["dtstart_utc"] is not None
        assert result["tz"] == "America/Toronto"
        
        # Duration should not be computed without end time
        assert "duration" not in result or result.get("duration") is None
    
    def test_compute_event_with_custom_timezone(self):
        """Test computing fields with custom timezone."""
        event_data = {
            "title": "Test Event",
            "dtstart": "2025-11-05 17:00:00",
            "tz": "America/New_York",
            "location": "New York",
        }
        
        result = compute_event_fields(event_data)
        
        assert result["tz"] == "America/New_York"
        assert result["dtstart_utc"] is not None
    
    def test_duration_calculation(self):
        """Test that duration is calculated correctly."""
        event_data = {
            "title": "Test Event",
            "dtstart": "2025-11-05 17:00:00",
            "dtend": "2025-11-05 19:00:00",
        }
        
        result = compute_event_fields(event_data)
        
        # Duration should be 2 hours
        assert result["duration"] == timedelta(hours=2)

