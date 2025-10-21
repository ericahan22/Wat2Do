"""
Views for the core app.
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
                "POST /api/auth/signup/": "Register a new user account with email",
                "POST /api/auth/login/": "Login with email and password (creates session)",
                "GET /api/auth/me/": "Get current user info (requires login)",
                "POST /api/auth/logout/": "Logout (destroys session)",
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


@csrf_exempt
def signup_view(request):
    """Register a new user account with email"""
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    
    if not email or not password:
        return JsonResponse({"error": "email+password required"}, status=400)
    
    # Check for duplicate email
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "email already registered"}, status=400)
    
    try:
        # Create user (username = email)
        user = User.objects.create_user(username=email, email=email, password=password)
        return JsonResponse({"ok": True, "id": user.id, "email": user.email})
    except Exception as e:
        return JsonResponse({"error": f"Failed to create user: {e!s}"}, status=500)


@csrf_exempt
def login_email_view(request):
    """Login with email and password"""
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    
    if not email or not password:
        return JsonResponse({"error": "email+password required"}, status=400)
    
    # Authenticate using username=email since that's what we set on signup
    user = authenticate(request, username=email, password=password)
    if not user:
        return JsonResponse({"error": "invalid credentials"}, status=401)
    
    login(request, user)
    return JsonResponse({"ok": True, "user": {"id": user.id, "email": user.email}})


def me_view(request):
    """Get current user info"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "not authenticated"}, status=401)
    
    u = request.user
    return JsonResponse({"id": u.id, "email": u.email})


def logout_view(request):
    """Logout current user"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "not authenticated"}, status=401)
    
    logout(request)
    return JsonResponse({"ok": True})
