import hashlib
import uuid
import base64
import os
from cryptography.fernet import Fernet
from django.db import models


class NewsletterSubscriber(models.Model):
    email_encrypted = models.TextField(unique=True, null=True, blank=True, help_text="AES encrypted email address")
    email_hash = models.CharField(
        max_length=128, unique=True, help_text="SHA-256 hash of the email for lookup"
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
    def _get_encryption_key():
        """Get or create encryption key from environment variable"""
        key = os.getenv('NEWSLETTER_ENCRYPTION_KEY')
        if not key:
            # Generate a new key if none exists (for development)
            key = Fernet.generate_key()
            print(f"WARNING: Generated new encryption key. Set NEWSLETTER_ENCRYPTION_KEY={key.decode()} in your environment")
        else:
            key = key.encode()
        return Fernet(key)

    @staticmethod
    def hash_email(email):
        """Create a SHA-256 hash of the email address for lookup"""
        return hashlib.sha256(email.lower().strip().encode("utf-8")).hexdigest()

    @staticmethod
    def encrypt_email(email):
        """Encrypt email address using AES encryption"""
        fernet = NewsletterSubscriber._get_encryption_key()
        encrypted_email = fernet.encrypt(email.lower().strip().encode())
        return base64.b64encode(encrypted_email).decode()

    @staticmethod
    def decrypt_email(encrypted_email):
        """Decrypt email address using AES decryption"""
        fernet = NewsletterSubscriber._get_encryption_key()
        encrypted_data = base64.b64decode(encrypted_email.encode())
        decrypted_email = fernet.decrypt(encrypted_data)
        return decrypted_email.decode()

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
        email_encrypted = cls.encrypt_email(email)
        return cls.objects.create(email_encrypted=email_encrypted, email_hash=email_hash, is_active=True)

    def get_email(self):
        """Get the decrypted email address"""
        return self.decrypt_email(self.email_encrypted)

    def get_email_display(self):
        """Return a masked version of the email for display purposes"""
        email = self.get_email()
        if '@' in email:
            local, domain = email.split('@', 1)
            return f"{local[:2]}***@{domain}"
        return f"{email[:2]}***@***"
