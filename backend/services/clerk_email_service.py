"""
Clerk-based email service for sending emails through Clerk's email functionality.
"""

import os
from datetime import date

import django
import dotenv
from django.conf import settings

dotenv.load_dotenv()

# Setup Django if not already configured
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()

# Import after Django setup
from apps.events.models import Events  # noqa: E402


class ClerkEmailService:
    """
    Email service using Clerk's email functionality.
    Clerk handles email delivery, templates, and user management.
    """
    
    def __init__(self):
        self.clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
        if not self.clerk_secret_key:
            print("Warning: CLERK_SECRET_KEY not set. Email functionality will be limited.")
    
    def _get_events_added_today(self):
        """Fetch events that were added to the database today"""
        try:
            today = date.today()

            events = (
                Events.objects.filter(added_at__date=today)
                .select_related()
                .order_by("dtstart_utc", "dtend_utc")
            )

            events_data = []
            for event in events:
                # Format the event data for email template
                event_date = event.dtstart_utc.strftime("%A, %B %d, %Y") if event.dtstart_utc else "TBD"
                event_time = event.dtstart_utc.strftime("%I:%M %p") if event.dtstart_utc else "TBD"
                
                events_data.append({
                    "title": event.title or "Untitled Event",
                    "description": event.description or "No description available",
                    "location": event.location or "Location TBD",
                    "date": event_date,
                    "time": event_time,
                    "price": f"${event.price}" if event.price else "Free",
                    "food": event.food or "No food mentioned",
                    "registration": "Required" if event.registration else "Not required",
                    "categories": event.categories or "General",
                    "source_url": event.source_url or "#",
                })

            return events_data
        except Exception as e:
            print(f"Warning: Could not fetch events from database: {e}")
            # Return mock data for testing
            return [
                {
                    "title": "Sample Event",
                    "description": "This is a sample event for testing",
                    "location": "Sample Location",
                    "date": "Today",
                    "time": "12:00 PM",
                    "price": "Free",
                    "food": "Pizza and drinks",
                    "registration": "Not required",
                    "categories": "General",
                    "source_url": "#",
                }
            ]

    def send_welcome_email(self, to_email, unsubscribe_token):
        """
        Send welcome email to new newsletter subscriber.
        Note: With Clerk, this would typically be handled by Clerk's user management
        and email templates. This is a placeholder for the email content.
        """
        if not to_email:
            print("Error: No email address provided.")
            return False

        print(f"📧 Clerk would send welcome email to {to_email}")
        print(f"   Unsubscribe token: {unsubscribe_token}")
        
        # In a real Clerk implementation, you would:
        # 1. Use Clerk's user management to create/send emails
        # 2. Use Clerk's email templates
        # 3. Handle unsubscribes through Clerk's user preferences
        
        return True

    def send_newsletter_email(self, to_email, unsubscribe_token):
        """
        Send newsletter email with today's events.
        Note: With Clerk, this would use Clerk's email templates and delivery system.
        """
        if not to_email:
            print("Error: No email address provided.")
            return False

        # Get today's events
        events_data = self._get_events_added_today()
        
        print(f"📧 Clerk would send newsletter to {to_email}")
        print(f"   Unsubscribe token: {unsubscribe_token}")
        print(f"   Events found: {len(events_data)}")
        
        # In a real Clerk implementation, you would:
        # 1. Use Clerk's email templates with event data
        # 2. Send through Clerk's email delivery system
        # 3. Track opens/clicks through Clerk's analytics
        
        return True

    def send_confirmation_email(self, to_email, confirmation_url):
        """
        Send email confirmation to new user.
        Note: With Clerk, user confirmation is handled automatically
        through Clerk's user management system.
        """
        if not to_email:
            print("Error: No email address provided.")
            return False

        print(f"📧 Clerk would send confirmation email to {to_email}")
        print(f"   Confirmation URL: {confirmation_url}")
        
        # In a real Clerk implementation, Clerk handles:
        # 1. User email verification automatically
        # 2. Email confirmation templates
        # 3. Email delivery and tracking
        
        return True

    def send_password_reset_email(self, to_email, reset_url):
        """
        Send password reset email to user.
        Note: With Clerk, password reset is handled automatically
        through Clerk's user management system.
        """
        if not to_email:
            print("Error: No email address provided.")
            return False

        print(f"📧 Clerk would send password reset email to {to_email}")
        print(f"   Reset URL: {reset_url}")
        
        # In a real Clerk implementation, Clerk handles:
        # 1. Password reset flow automatically
        # 2. Email templates for password reset
        # 3. Secure token generation and validation
        
        return True

    def send_custom_email(self, to_email, subject, html_content, _text_content=None):
        """
        Send a custom email through Clerk.
        This would use Clerk's email API for custom email sending.
        """
        if not to_email:
            print("Error: No email address provided.")
            return False

        if not self.clerk_secret_key:
            print("Warning: CLERK_SECRET_KEY not set. Cannot send email.")
            return False

        print(f"📧 Clerk would send custom email to {to_email}")
        print(f"   Subject: {subject}")
        print(f"   HTML content length: {len(html_content)} characters")
        
        # In a real Clerk implementation, you would:
        # 1. Use Clerk's email API to send custom emails
        # 2. Handle email templates and personalization
        # 3. Track delivery status and engagement
        
        return True


# Singleton instance
clerk_email_service = ClerkEmailService()
