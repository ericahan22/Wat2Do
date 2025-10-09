"""
Views for the app.
"""

from datetime import date, time

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import connection
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from services.openai_service import generate_embedding

from .embedding_utils import find_similar_events
from .filters import EventFilter
from .models import Clubs, Events, NewsletterSubscriber


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
                "POST /api/mock-event/": (
                    "Create a mock event with vector embedding (admin only)"
                ),
                "GET /api/test-similarity/?text=search_text": (
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
                    "Only admin users can access POST endpoints like /api/mock-event/"
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


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def get_events(request):
    """Get all events from database with optional filtering"""
    try:
        search_term = request.GET.get("search", "").strip()

        # Start with base queryset (ordering handled by model Meta)
        queryset = Events.objects.all()

        # Apply standard filters (dates, price, club_type, etc.)
        filterset = EventFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(
                {"error": "Invalid filter parameters", "details": filterset.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        filtered_queryset = filterset.qs

        # Apply vector similarity search if search term provided
        if search_term:
            search_embedding = generate_embedding(search_term)
            similar_events = find_similar_events(
                embedding=search_embedding, threshold=0.2
            )
            similar_event_ids = [event["id"] for event in similar_events]
            filtered_queryset = filtered_queryset.filter(id__in=similar_event_ids)
        else:
            filtered_queryset = Events.objects.none()

        # Return event IDs
        event_ids = [str(event.id) for event in filtered_queryset]
        return Response({"event_ids": event_ids})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def get_event_details(request):
    """Return event details for given comma-separated event IDs.

    Query params:
    - ids: comma-separated list of event IDs

    Response:
    {
      "events": [
        {
          "id": str,
          "name": str,
          "date": str (YYYY-MM-DD),
          "start_time": str (HH:MM:SS),
          "end_time": str (HH:MM:SS),
          "location": str,
          "url": str|null,
          "description": str|null
        }, ...
      ]
    }
    """
    try:
        ids_param = request.GET.get("ids", "").strip()
        if not ids_param:
            return Response(
                {"error": "Missing required query parameter: ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse ids and ensure they are integers
        try:
            id_list = [int(x) for x in ids_param.split(",") if x]
        except ValueError:
            return Response(
                {"error": "ids must be a comma-separated list of integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        events = Events.objects.filter(id__in=id_list)

        # Preserve input order
        event_map = {e.id: e for e in events}
        result = []
        for event_id in id_list:
            event = event_map.get(event_id)
            if not event:
                continue
            result.append(
                {
                    "id": str(event.id),
                    "name": event.name,
                    "date": event.date.isoformat(),
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat()
                    if event.end_time
                    else event.start_time.isoformat(),
                    "location": event.location,
                    "url": event.url,
                    "description": event.description,
                }
            )

        return Response({"events": result}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def get_clubs(request):
    """Get all clubs from database (no pagination)"""
    try:
        search_term = request.GET.get("search", "").strip()  # Get search term
        category_filter = request.GET.get("category", "").strip()  # Get category filter

        # Build base queryset
        base_queryset = Clubs.objects.all()

        # Apply filters to create filtered queryset
        filtered_queryset = base_queryset
        if search_term:
            filtered_queryset = filtered_queryset.filter(
                club_name__icontains=search_term
            )
        if category_filter and category_filter.lower() != "all":
            filtered_queryset = filtered_queryset.filter(
                categories__icontains=category_filter
            )

        # Convert to list of dictionaries
        clubs_data = [
            {
                "id": club.id,
                "club_name": club.club_name,
                "categories": club.categories,
                "club_page": club.club_page,
                "ig": club.ig,
                "discord": club.discord,
                "club_type": club.club_type,
            }
            for club in filtered_queryset
        ]

        return Response({"clubs": clubs_data})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAdminUser])
@throttle_classes([AnonRateThrottle])
def create_mock_event(request):
    """Create a mock event with vector embedding for testing"""
    try:
        # Get event data from request or use defaults
        event_data = {
            "name": request.data.get("name", "Test Event"),
            "location": request.data.get("location", "Test Location"),
            "food": request.data.get("food", "Pizza and drinks"),
            "club_handle": request.data.get("club_handle", "test_club"),
        }

        # Check if this would be a duplicate
        embedding = generate_embedding(event_data["description"])
        similar_events = find_similar_events(embedding, limit=1)

        if similar_events:
            return Response(
                {
                    "message": (
                        "Duplicate event detected! A similar event already exists."
                    ),
                    "event_data": event_data,
                    "similar_event": similar_events[0],
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Create the event using raw SQL to handle the vector column
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO events (
                    club_handle, url, name, date, start_time, end_time,
                    location, price, food, registration, image_url, embedding
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                RETURNING id
            """,
                [
                    event_data["club_handle"],
                    request.data.get("url", "https://example.com"),
                    event_data["name"],
                    request.data.get("date", date.today()),
                    request.data.get("start_time", time(18, 0)),  # 6 PM
                    request.data.get("end_time", time(20, 0)),  # 8 PM
                    event_data["location"],
                    request.data.get("price", 10.0),
                    event_data["food"],
                    request.data.get("registration", False),
                    request.data.get("image_url", "https://example.com/image.jpg"),
                    embedding,
                ],
            )

            event_id = cursor.fetchone()[0]

        return Response(
            {
                "message": "Mock event created successfully!",
                "event_id": event_id,
                "event_data": event_data,
                "embedding_generated": True,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to create mock event: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def test_similarity(request):
    """Test vector similarity search"""
    try:
        search_text = request.GET.get("text", "Test Event at Test Location")
        # Generate embedding for search text
        search_embedding = generate_embedding(search_text)

        similar_events = find_similar_events(search_embedding, threshold=0.38)

        results = []
        if similar_events:
            # Get the actual event details
            event_ids = [event["id"] for event in similar_events]
            events = Events.objects.filter(id__in=event_ids)
            # Create a mapping for quick lookup
            events_dict = {event.id: event for event in events}

            for similar_event in similar_events:
                event = events_dict.get(similar_event["id"])
                if event:
                    results.append(
                        {
                            "id": event.id,
                            "name": event.name,
                            "similarity": similar_event["similarity"],
                        }
                    )

        return Response({"search_text": search_text, "similar_events": results})

    except Exception as e:
        return Response(
            {"error": f"Failed to test similarity: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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


@api_view(["POST"])
@permission_classes([AllowAny])
def newsletter_subscribe(request):
    """Subscribe to the newsletter"""
    email = request.data.get("email")

    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate email format
    if "@" not in email or "." not in email:
        return Response(
            {"error": "Please provide a valid email address"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Check if already subscribed
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email.lower().strip(),
            defaults={"is_active": True},
        )

        if not created:
            if subscriber.is_active:
                return Response(
                    {"message": "You're already subscribed to our newsletter!"},
                    status=status.HTTP_200_OK,
                )
            else:
                # Reactivate subscription
                subscriber.is_active = True
                subscriber.save()

        # Send welcome email with mock events
        from services.email_service import email_service

        email_sent = email_service.send_welcome_email(
            subscriber.email, str(subscriber.unsubscribe_token)
        )

        if email_sent:
            return Response(
                {
                    "message": "Successfully subscribed! Check your email for upcoming events.",
                    "email": subscriber.email,
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "Subscribed successfully, but email could not be sent. Please check back later.",
                    "email": subscriber.email,
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

    except Exception as e:
        return Response(
            {"error": f"Failed to subscribe: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def newsletter_unsubscribe(request, token):
    """API endpoint for frontend unsubscribe functionality"""
    try:
        subscriber = NewsletterSubscriber.objects.get(unsubscribe_token=token)

        if request.method == "GET":
            # Return subscriber info for frontend
            return Response(
                {
                    "already_unsubscribed": not subscriber.is_active,
                    "email": subscriber.email,
                    "message": "Already unsubscribed"
                    if not subscriber.is_active
                    else "Ready to unsubscribe",
                    "unsubscribed_at": subscriber.unsubscribed_at,
                }
            )

        # POST - Process unsubscribe
        if not subscriber.is_active:
            return Response(
                {"error": "Already unsubscribed"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get reason and feedback
        reason = request.data.get("reason", "").strip()
        feedback = request.data.get("feedback", "").strip()
        full_reason = f"{reason} - {feedback}" if feedback else reason

        # Update subscriber
        subscriber.is_active = False
        subscriber.unsubscribe_reason = full_reason[:255]
        subscriber.unsubscribed_at = timezone.now()
        subscriber.save()

        return Response(
            {
                "message": "Successfully unsubscribed from the newsletter.",
                "email": subscriber.email,
                "unsubscribed_at": subscriber.unsubscribed_at,
            }
        )

    except NewsletterSubscriber.DoesNotExist:
        return Response(
            {"error": "Invalid unsubscribe token"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to process request: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
