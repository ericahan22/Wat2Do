"""
Views for the core app.
"""

import re
import secrets
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from services.email_service import email_service
from utils.encryption_utils import email_encryption


def validate_and_clear_token(user, token_field, error_message):
    """Helper function to validate token expiration and clear it"""
    token_data = getattr(user, token_field).split("|")
    if len(token_data) == 2:
        expiration_time = datetime.fromisoformat(token_data[1])
        if datetime.now() > expiration_time:
            # Token expired, clear it
            setattr(user, token_field, "")
            user.save()
            return False, f"{error_message} Please request a new one."
    return True, None


def validate_email_format(email):
    """Helper function to validate email format"""
    return re.match(r"^[^@]+@[^@]+\.[^@]+$", email) is not None


def create_success_response(message, user_data=None):
    """Helper function to create consistent success responses"""
    response = {"ok": True, "message": message}
    if user_data:
        response["user"] = user_data
    return response


@api_view(["GET"])
@permission_classes([AllowAny])
def home(_request):
    """Home endpoint with basic info"""
    return Response(
        {
            "message": "Instagram Event Scraper API with Vector Similarity",
            "endpoints": {
                "GET /api/events/?search=search_text": "Search events using vector similarity",
                "GET /api/clubs/": "Get all clubs from database",
                "GET /health/": "Health check",
                "POST /api/events/mock-event/": (
                    "Create a mock event with vector embedding (admin only)"
                ),
                "GET /api/events/test-similarity/?text=search_text": (
                    "Test vector similarity search"
                ),
                "POST /api/auth/signup/": "Register a new user account with email (sends confirmation email)",
                "POST /api/auth/login/": "Login with email and password (creates session)",
                "GET /api/auth/me/": "Get current user info (requires login)",
                "POST /api/auth/logout/": "Logout (destroys session)",
                "GET /api/auth/confirm/<token>/": "Confirm email address with token",
                "POST /api/auth/resend-confirmation/": "Resend confirmation email",
                "POST /api/auth/forgot-password/": "Request password reset email",
                "POST /api/auth/reset-password/<token>/": "Reset password with token",
            },
            "auth": {
                "info": "Uses session-based authentication. Login to access protected endpoints.",
                "admin_note": (
                    "Only admin users can access POST endpoints like /api/events/mock-event/"
                ),
                "signup_example": {
                    "email": "user@example.com",
                    "password": "your_password",
                },
                "login_example": {
                    "email": "user@example.com",
                    "password": "your_password",
                },
                "make_admin": (
                    "Use Django admin or manage.py createsuperuser to create admin users"
                ),
            },
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def health(_request):
    """Health check endpoint"""
    return Response({"status": "healthy", "message": "Server is running"})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """Get CSRF token for frontend"""
    from django.middleware.csrf import get_token

    csrf_token = get_token(request)
    return Response({"csrfToken": csrf_token})


@api_view(["POST"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="5/hr", block=True)
def signup(request):
    """Register a new user account with email"""

    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")

    if not email or not password:
        return Response(
            {"error": "email+password required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Email validation
    if not validate_email_format(email):
        return Response(
            {"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Check for duplicate email using username hash
    username_hash = email_encryption.create_email_hash(email)
    if User.objects.filter(username=username_hash).exists():
        return Response(
            {"error": "email already registered"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create user with encrypted email and hashed username
        user = email_encryption.create_user_with_encryption(email, password)

        confirmation_token = secrets.token_urlsafe(32)
        expiration_time = (datetime.now() + timedelta(hours=24)).isoformat()
        user.first_name = f"{confirmation_token}|{expiration_time}"
        user.save()

        # Send confirmation email
        base_url = settings.BASE_URL
        confirmation_url = f"{base_url}/api/auth/confirm/{confirmation_token}/"
        email_sent = email_service.send_confirmation_email(email, confirmation_url)

        if email_sent:
            return Response(
                {
                    "ok": True,
                    "message": "Account created! Please check your email to confirm your account.",
                    "id": user.id,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "ok": True,
                    "message": "Account created but confirmation email failed to send. Please try logging in.",
                    "id": user.id,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )
    except Exception as e:
        return Response(
            {"error": f"Failed to create user: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_email(request):
    """Login with email and password"""
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")

    if not email or not password:
        return Response(
            {"error": "email+password required"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = email_encryption.get_user_by_username_hash(email)
    if not user:
        return Response(
            {"error": "invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Authenticate using the found user
    if not user.check_password(password):
        return Response(
            {"error": "invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if user has confirmed their email
    if user.first_name and "|" in user.first_name:
        return Response(
            {"error": "Please confirm your email before logging in. Check your inbox for a confirmation email."}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, user)
    decrypted_email = email_encryption.decrypt_email(user.email)
    return Response(
        {"ok": True, "user": {"id": user.id, "email": decrypted_email}},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    """Get current user info"""
    u = request.user
    decrypted_email = email_encryption.decrypt_email(u.email)
    return Response({"id": u.id, "email": decrypted_email}, status=status.HTTP_200_OK)
    decrypted_email = email_encryption.decrypt_email(u.email)
    return Response({"id": u.id, "email": decrypted_email}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout current user"""
    from django.contrib.auth import logout as django_logout

    django_logout(request)
    return Response({"ok": True}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """Simple protected route that requires login"""
    return Response(
        {
            "message": "Welcome to the protected area!",
            "user": {
                "id": request.user.id,
                "email": request.user.email,
                "is_staff": request.user.is_staff,
                "is_superuser": request.user.is_superuser,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def confirm_email(request, token):
    """Confirm user's email address with token"""
    try:
        user = User.objects.get(first_name__startswith=token + "|")

        # Validate token expiration
        is_valid, error_msg = validate_and_clear_token(
            user, "first_name", "Confirmation token has expired."
        )
        if not is_valid:
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        # Clear the token and mark as confirmed
        user.first_name = ""
        user.save()

        # Automatically log them in
        login(request, user)

        # Redirect to frontend login page
        from django.http import HttpResponseRedirect

        return HttpResponseRedirect(settings.FRONTEND_URL + "/auth")
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid confirmation token"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"Confirmation failed: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@csrf_exempt
@api_view(["POST"])
@ratelimit(key="ip", rate="5/hr", block=True)
def resend_confirmation(request):
    """Resend confirmation email to user"""

    email = request.data.get("email", "").strip().lower()

    if not email:
        return Response({"error": "email required"}, status=status.HTTP_400_BAD_REQUEST)

    # Email validation
    if not validate_email_format(email):
        return Response(
            {"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)

        # Check if user is already confirmed (no token in first_name)
        if not user.first_name or "|" not in user.first_name:
            return Response(
                {"error": "Account is already confirmed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate new confirmation token with expiration (24 hours)
        confirmation_token = secrets.token_urlsafe(32)
        expiration_time = (datetime.now() + timedelta(hours=24)).isoformat()
        user.first_name = f"{confirmation_token}|{expiration_time}"
        user.save()

        # Send confirmation email
        base_url = settings.BASE_URL
        confirmation_url = f"{base_url}/api/auth/confirm/{confirmation_token}/"
        email_sent = email_service.send_confirmation_email(email, confirmation_url)

        if email_sent:
            return Response(
                {
                    "ok": True,
                    "message": "Confirmation email sent! Please check your email.",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "ok": False,
                    "message": "Failed to send confirmation email. Please try again later.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    except User.DoesNotExist:
        return Response({"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": f"Failed to resend confirmation: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="5/hr", block=True)
def forgot_password(request):
    """Send password reset email to user"""

    email = request.data.get("email", "").strip().lower()

    if not email:
        return Response({"error": "email required"}, status=status.HTTP_400_BAD_REQUEST)

    # Email validation
    if not validate_email_format(email):
        return Response(
            {"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = email_encryption.get_user_by_username_hash(email)
        if not user:
            # Don't reveal if email exists or not for security
            return Response(
                {
                    "ok": True,
                    "message": "If an account with this email exists, a password reset link has been sent.",
                },
                status=status.HTTP_200_OK,
            )

        # Generate reset token with expiration (1 hour)
        reset_token = secrets.token_urlsafe(32)
        expiration_time = (datetime.now() + timedelta(hours=1)).isoformat()
        user.last_name = f"{reset_token}|{expiration_time}"
        user.save()

        # Send reset email
        base_url = settings.BASE_URL
        reset_url = f"{base_url}/api/auth/reset-password/{reset_token}/"
        email_service.send_password_reset_email(email, reset_url)

        return Response(
            create_success_response(
                "If an account with this email exists, a password reset link has been sent."
            ),
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to process password reset: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request, token):
    """Reset user password with token"""

    new_password = request.data.get("password", "")

    if not new_password:
        return Response(
            {"error": "password required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if len(new_password) < 8:
        return Response(
            {"error": "password must be at least 8 characters"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(last_name__startswith=token + "|")

        # Validate token expiration
        is_valid, error_msg = validate_and_clear_token(
            user, "last_name", "Password reset token has expired."
        )
        if not is_valid:
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        # Clear the token and set new password
        user.last_name = ""
        user.set_password(new_password)
        user.save()

        # Automatically log them in
        login(request, user)

        return Response(
            create_success_response(
                "Password reset successfully! You are now logged in.",
                {"id": user.id, "email": email_encryption.decrypt_email(user.email)},
            ),
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return Response(
            {"error": "Invalid or expired password reset token"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"error": f"Password reset failed: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
