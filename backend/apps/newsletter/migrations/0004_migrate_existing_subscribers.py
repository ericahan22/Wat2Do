# Generated manually to handle existing subscribers

from django.db import migrations
from apps.newsletter.models import NewsletterSubscriber


def migrate_existing_subscribers(apps, schema_editor):
    """
    For existing subscribers, we can't recover their emails from the hash,
    so we'll mark them as needing to re-subscribe.
    """
    NewsletterSubscriber = apps.get_model('newsletter', 'NewsletterSubscriber')
    
    # Since we can't decrypt the hashed emails, we'll deactivate existing subscribers
    # and they'll need to re-subscribe
    existing_subscribers = NewsletterSubscriber.objects.filter(email_encrypted__isnull=True)
    
    for subscriber in existing_subscribers:
        # Mark as inactive so they need to re-subscribe
        subscriber.is_active = False
        subscriber.save()
    
    print(f"Deactivated {existing_subscribers.count()} existing subscribers. They will need to re-subscribe.")


def reverse_migrate_existing_subscribers(apps, schema_editor):
    """
    Reverse migration - reactivate subscribers
    """
    NewsletterSubscriber = apps.get_model('newsletter', 'NewsletterSubscriber')
    
    # Reactivate all subscribers
    NewsletterSubscriber.objects.update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0003_newslettersubscriber_email_encrypted_and_more'),
    ]

    operations = [
        migrations.RunPython(
            migrate_existing_subscribers,
            reverse_migrate_existing_subscribers,
        ),
    ]
