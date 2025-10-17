"""
Views for the core app.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


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
                    "Get authentication token with username/password"
                ),
            },
            "auth": {
                "info": "POST routes (except auth endpoints) require admin privileges",
                "header": "Authorization: Token <admin-token>",
                "admin_note": (
                    "Only admin users can access POST endpoints like /api/events/mock-event/"
                ),
                "register_example": {
                    "username": "your_username",
                    "password": "your_password",
                    "email": "optional@email.com",
                },
                "token_example": {
                    "username": "your_username",
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
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate user
        user = authenticate(username=username, password=password)
        if user:
            # Get or create token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "message": "Token created successfully"
                    if created
                    else "Token retrieved successfully",
                    "username": user.username,
                },
                status=status.HTTP_200_OK,
            )
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
    """Create a new user account (for development/testing purposes)"""
    try:
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create user
        user = User.objects.create_user(
            username=username, password=password, email=email
        )

        # Create token for the new user
        token = Token.objects.create(user=user)

        return Response(
            {
                "message": "User created successfully",
                "username": user.username,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to create user: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
