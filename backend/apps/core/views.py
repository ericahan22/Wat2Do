"""
Views for the core app with Clerk authentication.
"""

from apps.core.auth import jwt_required
from rest_framework import status
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
@jwt_required
def user_info(request):
    """Get current user info from Clerk"""
    user_id = request.user.get('id')
    return Response({
        "id": user_id,
        "email": request.user.get('email_addresses', [{}])[0].get('email_address'),
        "first_name": request.user.get('first_name'),
        "last_name": request.user.get('last_name'),
        "username": request.user.get('username'),
        "image_url": request.user.get('image_url'),
        "created_at": request.user.get('created_at'),
        "updated_at": request.user.get('updated_at'),
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@jwt_required
def protected_view(request):
    """Simple protected route that requires Clerk authentication"""
    user_id = request.user.get('id')
    return Response(
        {
            "message": "Welcome to the protected area!",
            "user": {
                "id": user_id,
                "email": request.user.get('email_addresses', [{}])[0].get('email_address'),
                "first_name": request.user.get('first_name'),
                "last_name": request.user.get('last_name'),
                "username": request.user.get('username'),
                "image_url": request.user.get('image_url'),
            },
        },
        status=status.HTTP_200_OK,
    )
