"""
Email Notification System - Test Script

This script allows you to test the email notification system without going through
the full event submission and approval workflow.

Usage:
    python test_email_notification.py user@example.com "Test Event" https://wat2do.ca/events/123

Requirements:
    - RESEND_API_KEY must be set in .env
    - RESEND_FROM_EMAIL must be set in .env
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from services.email_service import email_service


def test_approval_email(to_email, event_title, event_url, event_date=None, event_location=None):
    """Test sending an event approval email"""
    print(f"\n{'='*60}")
    print("Testing Event Approval Email Notification")
    print(f"{'='*60}\n")
    
    print(f"To: {to_email}")
    print(f"Event: {event_title}")
    print(f"URL: {event_url}")
    if event_date:
        print(f"Date: {event_date}")
    if event_location:
        print(f"Location: {event_location}")
    
    print("\nSending email...")
    
    success = email_service.send_event_approval_email(
        to_email=to_email,
        event_title=event_title,
        event_url=event_url,
        event_date=event_date,
        event_location=event_location
    )
    
    if success:
        print("\n✅ Email sent successfully!")
        print(f"Check {to_email} for the notification.")
    else:
        print("\n❌ Email failed to send.")
        print("Check the error messages above.")
    
    print(f"\n{'='*60}\n")
    return success


if __name__ == "__main__":
    # Check for required arguments
    if len(sys.argv) < 4:
        print("Usage: python test_email_notification.py <email> <event_title> <event_url> [event_date] [event_location]")
        print("\nExample:")
        print('  python test_email_notification.py user@example.com "Tech Talk" https://wat2do.ca/events/123 "January 15, 2026 at 6:00 PM" "DC 1302"')
        sys.exit(1)
    
    to_email = sys.argv[1]
    event_title = sys.argv[2]
    event_url = sys.argv[3]
    event_date = sys.argv[4] if len(sys.argv) > 4 else None
    event_location = sys.argv[5] if len(sys.argv) > 5 else None
    
    # Run the test
    test_approval_email(to_email, event_title, event_url, event_date, event_location)
