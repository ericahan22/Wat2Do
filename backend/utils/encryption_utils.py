"""
Encryption utilities for sensitive data like email addresses and user data.
Encryption utilities for sensitive data like email addresses and user data.
Uses Fernet (symmetric encryption) for encrypting/decrypting emails.
"""

import base64
import hashlib
import hmac
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

EMAIL_ENCRYPTION_KEY = os.getenv("EMAIL_ENCRYPTION_KEY")
EMAIL_HASH_KEY = os.getenv("EMAIL_HASH_KEY").encode("utf-8")


class EmailEncryption:
    """Handles encryption and decryption of email addresses and user data."""

    """Handles encryption and decryption of email addresses and user data."""

    def __init__(self):
        if not EMAIL_ENCRYPTION_KEY:
            raise ValueError("EMAIL_ENCRYPTION_KEY is not set")
        self.cipher = Fernet(EMAIL_ENCRYPTION_KEY)

    def encrypt_email(self, email):
        """Encrypt an email address."""
        if not email:
            return None

        # Normalize email (lowercase, strip whitespace)
        normalized_email = email.lower().strip()

        # Encrypt the email
        encrypted_bytes = self.cipher.encrypt(normalized_email.encode("utf-8"))

        # Return base64 encoded string for database storage
        return base64.b64encode(encrypted_bytes).decode("utf-8")

    def decrypt_email(self, encrypted_email):
        """Decrypt an email address."""
        if not encrypted_email:
            return None

        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_email.encode("utf-8"))

            # Decrypt
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)

            # Return as string
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            print(f"Error decrypting email: {e}")
            return None

    def create_email_hash(self, email):
        """Create a hash of the email for username field (SHA-256)."""
        normalized_email = email.lower().strip()
        return hashlib.sha256(normalized_email.encode("utf-8")).hexdigest()

    def create_hmac_email_hash(self, email):
        """Create HMAC hash of the email (for newsletter uniqueness)."""
        """Create a hash of the email for username field (SHA-256)."""
        normalized_email = email.lower().strip()
        return hashlib.sha256(normalized_email.encode("utf-8")).hexdigest()

    def create_hmac_email_hash(self, email):
        """Create HMAC hash of the email (for newsletter uniqueness)."""
        normalized_email = email.lower().strip()
        return hmac.new(
            EMAIL_HASH_KEY, normalized_email.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    # User-specific methods
    def create_user_with_encryption(self, email, password):
        """Create a new user with encrypted email and hashed username."""
        from django.contrib.auth.models import User

        # Hash email for username
        username = self.create_email_hash(email)

        # Encrypt email for storage
        encrypted_email = self.encrypt_email(email)

        # Create user
        user = User.objects.create_user(
            username=username, email=encrypted_email, password=password
        )

        return user

    def get_user_by_email(self, email):
        """Find user by original email (decrypts and compares)."""
        from django.contrib.auth.models import User

        email_lower = email.lower()

        # Search through all users to find matching email
        for user in User.objects.all():
            try:
                decrypted_email = self.decrypt_email(user.email)
                if decrypted_email == email_lower:
                    return user
            except Exception:
                continue

        return None

    def get_user_by_username_hash(self, email):
        """Find user by username hash (faster lookup)."""
        from django.contrib.auth.models import User

        username_hash = self.create_email_hash(email)
        try:
            return User.objects.get(username=username_hash)
        except User.DoesNotExist:
            return None

    def update_user_email(self, user, new_email):
        """Update user's email with encryption."""
        user.email = self.encrypt_email(new_email)
        user.username = self.create_email_hash(new_email)
        user.save()
        return user


# Global instance
email_encryption = EmailEncryption()
