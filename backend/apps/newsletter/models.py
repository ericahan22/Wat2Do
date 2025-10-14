import hashlib
import uuid

from django.db import models

from utils.encryption_utils import email_encryption


class NewsletterSubscriber(models.Model):
    email_encrypted = models.TextField(help_text="Encrypted email address")
    email_hash = models.CharField(
        max_length=128,
        unique=True,
        help_text="SHA-256 hash of the email for uniqueness checks",
    )
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
        return f"NewsletterSubscriber({self.email_hash[:8]}...)"

    @staticmethod
    def hash_email(email):
        """Create a SHA-256 hash of the email address for uniqueness checks"""
        return hashlib.sha256(email.lower().strip().encode("utf-8")).hexdigest()

    @classmethod
    def get_by_email(cls, email):
        """Get subscriber by email address (using hash lookup)"""
        email_hash = cls.hash_email(email)
        try:
            return cls.objects.get(email_hash=email_hash)
        except cls.DoesNotExist:
            return None

    @classmethod
    def create_subscriber(cls, email):
        """Create a new subscriber with encrypted email"""
        email_hash = cls.hash_email(email)
        email_encrypted = email_encryption.encrypt_email(email)
        return cls.objects.create(
            email_encrypted=email_encrypted, email_hash=email_hash, is_active=True
        )

    def get_email(self):
        """Decrypt and return the actual email address"""
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
