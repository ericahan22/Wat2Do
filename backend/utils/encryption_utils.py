"""
Encryption utilities for sensitive data like email addresses.
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
    """Handles encryption and decryption of email addresses."""

    def __init__(self):
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
        normalized_email = email.lower().strip()
        return hmac.new(
            EMAIL_HASH_KEY, normalized_email.encode("utf-8"), hashlib.sha256
        ).hexdigest()


# Global instance
email_encryption = EmailEncryption()
