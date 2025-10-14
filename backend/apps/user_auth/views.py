"""
Views for the core app.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import UserProfile
from services.email_verification_service import email_verification_service


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
                "POST /api/auth/register/": "Register a new user account",
                "POST /api/auth/token/": (
                        "Get authentication token with email/password"
                ),
            },
            "auth": {
                "info": "POST routes (except auth endpoints) require admin privileges",
                "header": "Authorization: Token <admin-token>",
                "admin_note": (
                    "Only admin users can access POST endpoints like /api/events/mock-event/"
                ),
                "register_example": {
                    "email": "your@uwaterloo.ca",
                    "password": "your_password",
                    "email": "optional@email.com",
                },
                "token_example": {
                    "email": "your@uwaterloo.ca",
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


@api_view(["POST"])
@permission_classes([AllowAny])
def create_auth_token(request):
    """Create or retrieve an authentication token for a user"""
    try:
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate user (using email as username)
        user = authenticate(username=email, password=password)
        if user:
            # Check if email is verified
            try:
                profile = user.profile
                if not profile.email_verified:
                    return Response(
                        {
                            "error": "Email not verified",
                            "message": "Please check your email and click the verification link to activate your account.",
                            "email_verified": False,
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            except UserProfile.DoesNotExist:
                return Response(
                    {"error": "User profile not found. Please contact support."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Get or create token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            # Create response with user data
            response = Response(
                {
                    "message": "Login successful",
                    "email": user.email,
                    "is_admin": user.is_staff and user.is_superuser,
                    "email_verified": True,
                },
                status=status.HTTP_200_OK,
            )
            
            # Set httponly secure cookie
            response.set_cookie(
                'auth_token',
                token.key,
                max_age=30*24*60*60,  # 30 days
                httponly=True,
                secure=not settings.DEBUG,  # Only secure in production
                samesite='Lax',
                domain='localhost'  # Set domain to localhost for cross-origin access
            )
            
            return response
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

    except Exception as e:
        return Response(
            {"error": f"Failed to create token: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def create_user(request):
    """Create a new user account with UWaterloo email verification"""
    try:
        password = request.data.get("password")
        email = request.data.get("email", "")

        if not password or not email:
            return Response(
                {"error": "Password and email are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate UWaterloo email
        if not email.endswith("@uwaterloo.ca"):
            return Response(
                {"error": "Email must be a valid UWaterloo email (@uwaterloo.ca)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create user with email as username
        user = User.objects.create_user(
            username=email, password=password, email=email
        )

        # Get the user profile (created automatically by signal)
        profile = user.profile

        # Generate verification token
        verification_token = email_verification_service.generate_verification_token()
        profile.verification_token = verification_token
        profile.verification_token_created = timezone.now()
        profile.save()

        # Send verification email
        email_sent = email_verification_service.send_verification_email(
            email=email,
            token=verification_token
        )

        if not email_sent:
            return Response(
                {"error": "Failed to send verification email. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "User created successfully. Please check your email to verify your account.",
                "email": user.email,
                "email_verified": False,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to create user: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def verify_email(request, token):
    """Verify user email with token"""
    try:
        # Find user profile with this token
        try:
            profile = UserProfile.objects.get(verification_token=token)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Invalid verification token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if token is expired (24 hours)
        if profile.verification_token_created:
            token_age = timezone.now() - profile.verification_token_created
            if token_age.total_seconds() > 24 * 60 * 60:  # 24 hours
                return Response(
                    {"error": "Verification token has expired. Please request a new one."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Check if already verified
        if profile.email_verified:
            return Response(
                {"message": "Email already verified"},
                status=status.HTTP_200_OK,
            )

        # Mark as verified and clear token
        profile.email_verified = True
        profile.verification_token = None
        profile.verification_token_created = None
        profile.save()

        # Get frontend URL from environment
        import os
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        submit_url = f"{frontend_url}/submit"
        
        # Return HTML redirect response
        from django.http import HttpResponse
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Email Verified - Wat2Do</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f8f9fa; }}
                .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .success {{ color: #28a745; font-size: 24px; margin-bottom: 20px; }}
                .message {{ color: #333; margin-bottom: 30px; }}
                .button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; }}
                .button:hover {{ background-color: #0056b3; }}
            </style>
            <script>
                // Auto-redirect after 3 seconds
                setTimeout(function() {{
                    window.location.href = "{submit_url}";
                }}, 3000);
            </script>
        </head>
        <body>
            <div class="container">
                <div class="success">✅ Email Verified Successfully!</div>
                <div class="message">
                    <p>Your email has been verified. You can now log in and start submitting events and clubs.</p>
                    <p>Redirecting you to the submit page in 3 seconds...</p>
                </div>
                <a href="{submit_url}" class="button">Go to Submit Page</a>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content, content_type='text/html')

    except Exception as e:
        return Response(
            {"error": f"Failed to verify email: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def check_verification_status(request):
    """Check if user's email is verified"""
    try:
        email = request.GET.get("email")
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account found with this email address"},
                status=status.HTTP_404_NOT_FOUND,
            )

        profile = user.profile
        return Response(
            {
                "email_verified": profile.email_verified,
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to check verification status: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_verification(request):
    """Resend verification email"""
    try:
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account found with this email address"},
                status=status.HTTP_404_NOT_FOUND,
            )

        profile = user.profile

        # Check if already verified
        if profile.email_verified:
            return Response(
                {"message": "Email is already verified"},
                status=status.HTTP_200_OK,
            )

        # Generate new verification token
        verification_token = email_verification_service.generate_verification_token()
        profile.verification_token = verification_token
        profile.verification_token_created = timezone.now()
        profile.save()

        # Send verification email
        email_sent = email_verification_service.send_resend_verification_email(
            email=email,
            token=verification_token
        )

        if not email_sent:
            return Response(
                {"error": "Failed to send verification email. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Verification email sent successfully. Please check your email."},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to resend verification: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def check_auth_status(request):
    """Check if user is authenticated via cookie"""
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            profile = request.user.profile
            return Response(
                {
                    "authenticated": True,
                    "email": request.user.email,
                    "is_admin": request.user.is_staff and request.user.is_superuser,
                    "email_verified": profile.email_verified,
                },
                status=status.HTTP_200_OK,
            )
        except UserProfile.DoesNotExist:
            return Response(
                {"authenticated": False, "error": "User profile not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    else:
        return Response(
            {"authenticated": False},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
def logout(request):
    """Logout user by clearing auth cookie"""
    response = Response(
        {"message": "Logged out successfully"},
        status=status.HTTP_200_OK,
    )
    
    # Clear the auth cookie
    response.delete_cookie('auth_token')
    
    return response
