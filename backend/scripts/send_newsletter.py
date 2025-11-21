#!/usr/bin/env python
"""
Send newsletter emails to all active subscribers.
For now, sends mock event data. In the future, will send real upcoming events.
"""

import os
import sys

import django

# Add the parent directory to the path so we can import Django modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

# Import Django modules after setup
from apps.newsletter.models import NewsletterSubscriber  # noqa: E402
from services.email_service import email_service  # noqa: E402
from scraping.logging_config import logger  # noqa: E402


def send_newsletter_to_all():
    """Send newsletter to all active subscribers"""

    # Get all active subscribers
    active_subscribers = NewsletterSubscriber.objects.filter(is_active=True)

    total_subscribers = active_subscribers.count()
    logger.info(f"📧 Starting newsletter send to {total_subscribers} active subscribers...")

    if total_subscribers == 0:
        logger.warning("⚠️  No active subscribers found.")
        return

    success_count = 0
    failed_count = 0
    failed_emails = []

    def send_to_subscriber(subscriber):
        """Send email to a single subscriber, return success status"""
        try:
            # Get the email address, handle decryption failures
            email_address = subscriber.get_email()
            if not email_address:
                return False, "Failed to decrypt email address"

            # Use Resend-backed newsletter email service
            email_sent = email_service.send_newsletter_email(
                email_address, str(subscriber.unsubscribe_token)
            )
            return email_sent, None
        except Exception as e:
            return False, str(e)

    for subscriber in active_subscribers:
        email_sent, error = send_to_subscriber(subscriber)

        if email_sent:
            success_count += 1
            logger.info("✅ Email sent successfully")
        else:
            failed_count += 1
            failed_emails.append(subscriber.get_email())
            if error:
                logger.error(f"❌ Error sending email: {error}")
            else:
                logger.error("❌ Failed to send email")

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 Newsletter Send Summary")
    logger.info("=" * 60)
    logger.info(f"Total subscribers: {total_subscribers}")
    logger.info(f"✅ Successfully sent: {success_count}")
    logger.info(f"❌ Failed: {failed_count}")

    if failed_emails:
        logger.warning(f"\n⚠️  {len(failed_emails)} emails failed to send")

    logger.info("=" * 60)

    # Return non-zero exit code if any emails failed
    if failed_count > 0:
        sys.exit(1)

    logger.info("\n🎉 Newsletter send completed successfully!")


if __name__ == "__main__":
    send_newsletter_to_all()
