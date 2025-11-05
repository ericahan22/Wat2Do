"""
Date utilities for semester end times and date-related operations.
"""

from datetime import datetime


# Semester end times in format YYYYMMDDTHHMMSSZ (UTC)
# Index 0: Fall semester, Index 1: Winter semester, Index 2: Summer semester
UNIVERSITY_SEMESTER_END_TIMES = {
    "University of Waterloo": [
        "20251231T235959Z",  # Fall semester (ends December 31)
        "20260430T235959Z",  # Winter semester (ends April 30)
        "20260831T235959Z",  # Summer semester (ends August 31)
    ]
}


def get_current_semester_end_time(university: str = "University of Waterloo") -> str:
    """
    Get the end time of the current semester based on the current date.
    
    Args:
        university: The university name (default: "University of Waterloo")
    
    Returns:
        A string in format YYYYMMDDTHHMMSSZ representing the end of the current semester
    
    Semester breakdown:
    - Fall: September 1 - December 31
    - Winter: January 1 - April 30
    - Summer: May 1 - August 31
    """
    
    semester_end_times = UNIVERSITY_SEMESTER_END_TIMES[university]
    now = datetime.now()
    month = now.month
    
    # Determine current semester based on month
    if 1 <= month <= 4:
        # Winter semester (January - April)
        return semester_end_times[1]
    elif 5 <= month <= 8:
        # Summer semester (May - August)
        return semester_end_times[2]
    else:
        # Fall semester (September - December)
        return semester_end_times[0]

