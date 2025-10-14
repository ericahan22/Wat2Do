"""
Email verification service using Resend API.
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional

import resend
from django.conf import settings

logger = logging.getLogger(__name__)


class EmailVerificationService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        if not self.api_key:
            logger.warning("RESEND_API_KEY not found in environment variables")
        else:
            resend.api_key = self.api_key

    def generate_verification_token(self) -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)

    def send_verification_email(self, email: str, token: str) -> bool:
        """
        Send email verification email to user
        
        Args:
            email: User's email address
            token: Verification token
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.api_key:
            logger.error("Cannot send email: RESEND_API_KEY not configured")
            return False

        try:
            # Get the backend URL from settings or environment
            backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
            verification_url = f"{backend_url}/api/auth/verify-email/{token}"

            # Email template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Verify Your Email - Wat2Do</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px; }}
                    .content {{ padding: 20px; }}
                    .button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px; font-size: 14px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to Wat2Do!</h1>
                    </div>
                    <div class="content">
                        <h2>Hi there!</h2>
                        <p>Thank you for registering with Wat2Do. To complete your registration and start submitting events and clubs, please verify your email address by clicking the button below:</p>
                        
                        <div style="text-align: center;">
                            <a href="{verification_url}" class="button">Verify Email Address</a>
                        </div>
                        
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p><a href="{verification_url}">{verification_url}</a></p>
                        
                        <p><strong>Note:</strong> This link will expire in 24 hours for security reasons.</p>
                    </div>
                    <div class="footer">
                        <p>If you didn't create an account with Wat2Do, you can safely ignore this email.</p>
                        <p>© 2024 Wat2Do - University of Waterloo Event Discovery</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Send email via Resend
            params = {
                "from": "Wat2Do <noreply@wat2do.ca>",  # Update with your verified domain
                "to": [email],
                "subject": "Verify Your Email - Wat2Do",
                "html": html_content,
            }

            email_response = resend.Emails.send(params)
            
            # Check if email was sent successfully
            if email_response and (hasattr(email_response, 'id') or (isinstance(email_response, dict) and 'id' in email_response)):
                email_id = email_response.id if hasattr(email_response, 'id') else email_response.get('id')
                logger.info(f"Verification email sent successfully to {email} with ID: {email_id}")
                return True
            else:
                logger.error(f"Failed to send verification email to {email}: {email_response}")
                return False

        except Exception as e:
            logger.error(f"Error sending verification email to {email}: {str(e)}")
            return False

    def send_resend_verification_email(self, email: str, token: str) -> bool:
        """
        Send a resend verification email (same as send_verification_email but with different messaging)
        """
        if not self.api_key:
            logger.error("Cannot send email: RESEND_API_KEY not configured")
            return False

        try:
            backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
            verification_url = f"{backend_url}/api/auth/verify-email/{token}"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Resend Verification - Wat2Do</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px; }}
                    .content {{ padding: 20px; }}
                    .button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px; font-size: 14px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Wat2Do - Email Verification</h1>
                    </div>
                    <div class="content">
                        <h2>Hi there!</h2>
                        <p>You requested a new verification email for your Wat2Do account. Click the button below to verify your email address:</p>
                        
                        <div style="text-align: center;">
                            <a href="{verification_url}" class="button">Verify Email Address</a>
                        </div>
                        
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p><a href="{verification_url}">{verification_url}</a></p>
                        
                        <p><strong>Note:</strong> This link will expire in 24 hours for security reasons.</p>
                    </div>
                    <div class="footer">
                        <p>If you didn't request this email, you can safely ignore it.</p>
                        <p>© 2024 Wat2Do - University of Waterloo Event Discovery</p>
                    </div>
                </div>
            </body>
            </html>
            """

            params = {
                "from": "Wat2Do <noreply@wat2do.ca>",
                "to": [email],
                "subject": "Verify Your Email - Wat2Do (Resend)",
                "html": html_content,
            }

            email_response = resend.Emails.send(params)
            
            # Check if email was sent successfully
            if email_response and (hasattr(email_response, 'id') or (isinstance(email_response, dict) and 'id' in email_response)):
                email_id = email_response.id if hasattr(email_response, 'id') else email_response.get('id')
                logger.info(f"Resend verification email sent successfully to {email} with ID: {email_id}")
                return True
            else:
                logger.error(f"Failed to send resend verification email to {email}: {email_response}")
                return False

        except Exception as e:
            logger.error(f"Error sending resend verification email to {email}: {str(e)}")
            return False


# Singleton instance
email_verification_service = EmailVerificationService()
