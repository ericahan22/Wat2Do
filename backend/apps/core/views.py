"""
Views for the core app with Clerk authentication.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from clerk_django.permissions.clerk import ClerkAuthenticated


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
            },
            "auth": {
                "info": "Uses Clerk authentication. Include Bearer token in Authorization header.",
                "admin_note": (
                    "Only admin users can access POST endpoints like /api/events/mock-event/"
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
@permission_classes([ClerkAuthenticated])
def user_info(request):
    """Get current user info from Clerk"""
    user_id = request.clerk_user.get('id')
    return Response({
        "id": user_id,
        "email": request.clerk_user.get('email_addresses', [{}])[0].get('email_address'),
        "first_name": request.clerk_user.get('first_name'),
        "last_name": request.clerk_user.get('last_name'),
        "username": request.clerk_user.get('username'),
        "image_url": request.clerk_user.get('image_url'),
        "created_at": request.clerk_user.get('created_at'),
        "updated_at": request.clerk_user.get('updated_at'),
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([ClerkAuthenticated])
def protected_view(request):
    """Simple protected route that requires Clerk authentication"""
    user_id = request.clerk_user.get('id')
    return Response(
        {
            "message": "Welcome to the protected area!",
            "user": {
                "id": user_id,
                "email": request.clerk_user.get('email_addresses', [{}])[0].get('email_address'),
                "first_name": request.clerk_user.get('first_name'),
                "last_name": request.clerk_user.get('last_name'),
                "username": request.clerk_user.get('username'),
                "image_url": request.clerk_user.get('image_url'),
            },
        },
        status=status.HTTP_200_OK,
    )