from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
import uuid

from services.openai_service import generate_embedding
from services.storage_service import storage_service
from utils.embedding_utils import find_similar_events
from utils.filters import EventFilter

from .models import Events
from .serializers import EventSubmissionSerializer, EventSubmissionResponseSerializer, EventModerationSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def get_events(request):
    """Get all events from database with optional filtering"""
    try:
        search_term = request.GET.get("search", "").strip()

        # Start with base queryset (ordering handled by model Meta)
        # Show approved events and scraped events to public (scraped events are auto-approved)
        queryset = Events.objects.filter(status__in=['approved', 'scraped'])

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
            start_date = request.GET.get("start_date")
            similar_events = find_similar_events(
                embedding=search_embedding, min_date=start_date
            )
            for event in similar_events:
                print(event["name"], event["similarity"])
            similar_event_ids = [event["id"] for event in similar_events]
            filtered_queryset = filtered_queryset.filter(id__in=similar_event_ids)

        # Return selected event fields (excluding description and embedding)
        fields = [
            "id",
            "club_handle",
            "url",
            "name",
            "date",
            "start_time",
            "end_time",
            "location",
            "price",
            "food",
            "registration",
            "image_url",
            "club_type",
            "added_at",
        ]
        results = list(filtered_queryset.values(*fields))
        return Response(results)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def test_similarity(request):
    """Test semantic similarity search using a search query"""
    try:
        search_query = request.GET.get("q")
        if not search_query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate embedding for the search query
        search_embedding = generate_embedding(search_query)

        # Test semantic search
        threshold = float(request.GET.get("threshold", 0.25))
        limit = int(request.GET.get("limit")) if request.GET.get("limit") else None
        similar_events = find_similar_events(
            search_embedding, threshold=threshold, limit=limit
        )

        return Response(
            {
                "search_query": search_query,
                "threshold": threshold,
                "limit": limit,
                "results": similar_events,
            }
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to test similarity: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def export_events_ics(request):
    """Export events as .ics file for calendar import.

    Query params:
    - ids: comma-separated list of event IDs

    Returns: .ics file with Content-Type: text/calendar
    """
    from django.http import HttpResponse

    try:
        ids_param = request.GET.get("ids", "").strip()
        if not ids_param:
            return Response(
                {"error": "Missing required query parameter: ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse ids
        try:
            id_list = [int(x) for x in ids_param.split(",") if x]
        except ValueError:
            return Response(
                {"error": "ids must be a comma-separated list of integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        events = Events.objects.filter(id__in=id_list)

        if not events.exists():
            return Response(
                {"error": "No events found with the provided IDs"},
                status=status.HTTP_404_NOT_FOUND,
            )

        ics_content = _generate_ics_content(events)

        response = HttpResponse(
            ics_content, content_type="text/calendar; charset=utf-8"
        )
        response["Content-Disposition"] = 'attachment; filename="events.ics"'
        response["Cache-Control"] = "private, max-age=0, must-revalidate"

        return response

    except Exception as e:
        return Response(
            {"error": f"Failed to export events: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _generate_ics_content(events):
    """Generate ICS file content from events."""

    def escape_text(text):
        """Escape special characters in Calendar format."""
        if not text:
            return ""
        return (
            text.replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\n", "\\n")
        )

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Wat2Do//Events//EN",
        "CALSCALE:GREGORIAN",
    ]

    # Current timestamp in UTC for DTSTAMP
    from datetime import datetime

    now = datetime.utcnow()
    dtstamp = now.strftime("%Y%m%dT%H%M%SZ")

    for event in events:
        start_date = event.date.strftime("%Y%m%d")
        start_time = event.start_time.strftime("%H%M%S")
        end_time = event.end_time.strftime("%H%M%S") if event.end_time else start_time

        lines.append("BEGIN:VEVENT")
        lines.append(f"DTSTART:{start_date}T{start_time}")
        lines.append(f"DTEND:{start_date}T{end_time}")
        lines.append(f"DTSTAMP:{dtstamp}")
        lines.append(f"SUMMARY:{escape_text(event.name)}")

        if event.description:
            lines.append(f"DESCRIPTION:{escape_text(event.description)}")

        if event.location:
            lines.append(f"LOCATION:{escape_text(event.location)}")

        if event.url:
            lines.append(f"URL:{event.url}")

        lines.append(f"UID:{event.id}@wat2do.com")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def get_google_calendar_urls(request):
    """Generate Google Calendar URLs for given event IDs.

    Query params:
    - ids: comma-separated list of event IDs

    Returns:
    {
      "urls": ["https://calendar.google.com/calendar/render?...", ...]
    }
    """
    try:
        ids_param = request.GET.get("ids", "").strip()
        if not ids_param:
            return Response(
                {"error": "Missing required query parameter: ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse ids
        try:
            id_list = [int(x) for x in ids_param.split(",") if x]
        except ValueError:
            return Response(
                {"error": "ids must be a comma-separated list of integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(id_list) == 0:
            return Response(
                {"error": "No valid event IDs provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch events
        events = Events.objects.filter(id__in=id_list)

        if not events.exists():
            return Response(
                {"error": "No events found with the provided IDs"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Generate Google Calendar URLs
        urls = []
        from urllib.parse import urlencode

        for event in events:
            # Format dates for Google Calendar (YYYYMMDDTHHMMSS)
            start_date = event.date.strftime("%Y%m%d")
            start_time = event.start_time.strftime("%H%M%S")
            end_time = (
                event.end_time.strftime("%H%M%S") if event.end_time else start_time
            )

            start_datetime = f"{start_date}T{start_time}"
            end_datetime = f"{start_date}T{end_time}"

            # Build details field
            details_parts = []
            if event.description:
                details_parts.append(event.description)
            if event.url:
                details_parts.append(event.url)
            details = "\n\n".join(details_parts)

            # Build Google Calendar URL
            params = {
                "action": "TEMPLATE",
                "text": event.name,
                "dates": f"{start_datetime}/{end_datetime}",
                "details": details,
                "location": event.location or "",
            }

            google_calendar_url = (
                f"https://calendar.google.com/calendar/render?{urlencode(params)}"
            )
            urls.append(google_calendar_url)

        return Response({"urls": urls}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": f"Failed to generate Google Calendar URLs: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_event(request):
    """Submit a new event for approval"""
    try:
        # Check if user's email is verified
        try:
            profile = request.user.profile
            if not profile.email_verified:
                return Response(
                    {"error": "Email verification required. Please verify your email before submitting events."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except:
            return Response(
                {"error": "User profile not found. Please contact support."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Handle image upload
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"error": "Image is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Upload image to S3
        file_ext = image_file.name.split('.')[-1] if '.' in image_file.name else 'jpg'
        filename = f"events/submitted/{uuid.uuid4()}.{file_ext}"
        
        image_data = image_file.read()
        image_url = storage_service.upload_image_data(image_data, filename)
        
        if not image_url:
            return Response(
                {"error": "Failed to upload image"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
        # Prepare data for serializer
        data = request.data.copy()
        data['image_url'] = image_url
        
        # Validate and create event
        serializer = EventSubmissionSerializer(data=data)
        if serializer.is_valid():
            # Generate embedding from description
            description = serializer.validated_data.get('description', '')
            embedding = generate_embedding(description) if description else None
            
            # Create event with submission fields
            event = serializer.save(
                status='pending',
                submitted_by=request.user,
                submitted_at=timezone.now(),
                embedding=embedding
            )
            
            response_serializer = EventSubmissionResponseSerializer(event)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {"error": f"Failed to submit event: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_submissions(request):
    """Get user's submitted events"""
    try:
        events = Events.objects.filter(
            submitted_by=request.user,
            status__in=['pending', 'approved', 'rejected']
        ).order_by('-submitted_at')
        
        serializer = EventSubmissionResponseSerializer(events, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {"error": f"Failed to get submissions: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_pending_submissions(request):
    """Admin: Get all pending event submissions"""
    try:
        events = Events.objects.filter(status='pending').order_by('submitted_at')
        serializer = EventSubmissionResponseSerializer(events, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {"error": f"Failed to get pending submissions: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def moderate_event(request, event_id):
    """Admin: Approve or reject an event submission"""
    try:
        try:
            event = Events.objects.get(id=event_id, status='pending')
        except Events.DoesNotExist:
            return Response(
                {"error": "Event not found or not pending"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = EventModerationSerializer(data=request.data)
        if serializer.is_valid():
            # Update event with moderation decision
            event.status = serializer.validated_data['status']
            event.reviewed_by = request.user
            event.reviewed_at = timezone.now()
            
            if serializer.validated_data['status'] == 'rejected':
                event.rejection_reason = serializer.validated_data['rejection_reason']
            
            event.save()
            
            response_serializer = EventSubmissionResponseSerializer(event)
            return Response(response_serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {"error": f"Failed to moderate event: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
