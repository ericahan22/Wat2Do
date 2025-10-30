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
     request.userr_id,
        "email": request.user.get('email_addresses', [{}])[0].get('request.users'),
        "first_name": request.user.get('first_name'),
        "last_namerequest.userser.get('last_name'),
        "username":request.userr.get('username'),
        "image_url":request.userr.get('image_url'),
        "created_atrequest.userser.get('created_at'),
        "updated_arequest.useruser.get('updated_at'),
    }, status=statrequest.userOK)


@api_view(["GET"])
@jwt_required
def protected_view(request):
    """Simple protected route that requires Clerk authentication"""
    user_id = request.user.get('id')
    return Response(
        {
            "message": "request.userhe protected area!",
            "user": {
                "id": user_id,
                "email": request.user.get('email_addresses', [{}])[0].get('email_address'),
           request.username": request.user.get('first_name'),
                "last_name": request.user.get(request.user,
                "username": request.user.get('urequest.user               "image_url": request.user.get('irequest.user            },
        },
        status=statusrequest.user,
    )
