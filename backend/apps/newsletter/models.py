import uuid

from django.db import models

from utils.encryption_utils import email_encryption


class NewsletterSubscriber(models.Model):
    email_encrypted = models.TextField(help_text="Encrypted email address")
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    unsubscribe_token = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False
    )
    unsubscribe_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Reason provided when user unsubscribed",
    )
    unsubscribed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "newsletter_subscribers"
        ordering = ["-subscribed_at"]

    def __str__(self):
        return f"NewsletterSubscriber({self.get_email_display()})"

    @classmethod
    def get_by_email(cls, email):
        """Get subscriber by email"""
        encrypted_email = email_encryption.encrypt_email(email)
        return cls.objects.get(email_encrypted=encrypted_email)

    @classmethod
    def create_subscriber(cls, email):
        """Create a new subscriber for an email"""
        encrypted_email = email_encryption.encrypt_email(email)
        return cls.objects.create(email_encrypted=encrypted_email, is_active=True)

    def get_email(self):
        """Get the email (decrypted)"""

        return email_encryption.decrypt_email(self.email_encrypted)

    def get_email_display(self):
        """Return a masked version of the email for display purposes"""
        email = self.get_email()
        if email:
            # Show first 2 chars and domain
            local, domain = email.split("@", 1)
            masked_local = (
                local[:2] + "*" * (len(local) - 2) if len(local) > 2 else local
            )
            return f"{masked_local}@{domain}"
        return "***@***"
