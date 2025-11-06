import uuid
from datetime import timedelta
import pytz

from apps.core.auth import jwt_required, admin_required, optional_jwt
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.html import escape
from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from services.openai_service import extract_events_from_caption, generate_embedding
from services.storage_service import storage_service
from utils import events_utils
from utils.embedding_utils import find_similar_events
from utils.filters import EventFilter
from utils.submission_utils import compute_event_fields
from utils.validation import (
    validate_and_sanitize_event_data,
    validate_required_fields,
    USER_EDITABLE_FIELDS,
)

from .models import Events, EventSubmission, EventInterest, EventDates


@api_view(["GET"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="600/hr", block=True)
def get_events(request):
    """Get events with cursor-based pagination for infinite scroll"""
    try:
        search_term = request.GET.get("search", "").strip()
        dtstart_utc_param = request.GET.get("dtstart_utc", "").strip()
        cursor = request.GET.get("cursor", "").strip()
        limit = int(request.GET.get("limit", "20"))
        all_events = request.GET.get("all", "").lower() == "true"  # For calendar view
        
        # Limit boundary check
        if limit > 100:
            limit = 100

        queryset = Events.objects.filter(
            status="CONFIRMED",
            school="University of Waterloo"
        )
        
        # Apply default upcoming events filter only if not provided in request
        if not dtstart_utc_param:
            now = timezone.now()
            two_half_hours_ago = now - timedelta(hours=2.5)
            queryset = queryset.filter(
                Q(dtend_utc__gte=now) | (Q(dtend_utc__isnull=True) & Q(dtstart_utc__gte=two_half_hours_ago))
            )
        
        queryset = queryset.order_by("dtstart_utc", "id")
        
        filterset = EventFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(
                {"error": "Invalid filter parameters", "details": filterset.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        filtered_queryset = filterset.qs

        if search_term:
            # Parse semicolon-separated filters (for OR query)
            search_terms = [
                term.strip() for term in search_term.split(";") if term.strip()
            ]

            # Build OR query: match any of the search terms in any field
            or_queries = Q()
            for term in search_terms:
                term_query = (
                    Q(title__icontains=term)
                    | Q(location__icontains=term)
                    | Q(description__icontains=term)
                    | Q(food__icontains=term)
                    | Q(club_type__icontains=term)
                    | Q(school__icontains=term)
                    | Q(ig_handle__icontains=term)
                    | Q(discord_handle__icontains=term)
                    | Q(x_handle__icontains=term)
                    | Q(tiktok_handle__icontains=term)
                    | Q(fb_handle__icontains=term)
                )
                or_queries |= term_query

            filtered_queryset = filtered_queryset.filter(or_queries)

        # Handle cursor-based pagination
        if cursor and not all_events:
            # Cursor format: "{dtstart_utc_iso}_{event_id}"
            try:
                cursor_parts = cursor.split("_")
                cursor_dtstart = cursor_parts[0]
                cursor_id = int(cursor_parts[1])
                
                # Filter events after cursor position
                filtered_queryset = filtered_queryset.filter(
                    Q(dtstart_utc__gt=cursor_dtstart) |
                    (Q(dtstart_utc=cursor_dtstart) & Q(id__gt=cursor_id))
                )
            except (ValueError, IndexError):
                return Response(
                    {"error": "Invalid cursor format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        fields = [
            "id",
            "title",
            "description",
            "location",
            "dtstart_utc",
            "dtend_utc",
            "price",
            "food",
            "registration",
            "source_image_url",
            "club_type",
            "added_at",
            "school",
            "source_url",
            "ig_handle",
            "discord_handle",
            "x_handle",
            "tiktok_handle",
            "fb_handle",
            "other_handle",
        ]
        
        # Get total count for the filtered queryset
        total_count = filtered_queryset.count()
        
        # Fetch one more than limit to check if there are more results
        if all_events:
            # Return all events for calendar view
            results = list(filtered_queryset.values(*fields))
            next_cursor = None
        else:
            # Paginated results
            results = list(filtered_queryset.values(*fields)[: limit + 1])
            
            # Determine if there's a next page
            has_more = len(results) > limit
            if has_more:
                results = results[:limit]  # Remove the extra item
                
                # Generate next cursor from last item
                last_event = results[-1]
                next_cursor = f"{last_event['dtstart_utc'].isoformat()}_{last_event['id']}"
            else:
                next_cursor = None

        # Get event IDs for bulk interest query
        event_ids = [event['id'] for event in results]
        
        # Get interest counts for all events in one query
        from django.db.models import Count
        interest_counts = EventInterest.objects.filter(
            event_id__in=event_ids
        ).values('event_id').annotate(count=Count('id'))
        interest_count_map = {item['event_id']: item['count'] for item in interest_counts}

        for event in results:
            event["display_handle"] = events_utils.determine_display_handle(event)
            event["interest_count"] = interest_count_map.get(event['id'], 0)

        return Response({
            "results": results,
            "nextCursor": next_cursor,
            "hasMore": next_cursor is not None,
            "totalCount": total_count
        })

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
@optional_jwt
@ratelimit(key="ip", rate="60/hr", block=True)
def get_event(request, event_id):
    """Get a single event by ID with upcoming dates"""
    try:
        fields = [
            "id", "title", "description", "location", "dtstart", "dtend",
            "dtstart_utc", "dtend_utc", "all_day", "price", "food", "registration",
            "source_image_url", "club_type", "added_at", "school", "status",
            "source_url", "ig_handle", "discord_handle", "x_handle",
            "tiktok_handle", "fb_handle", "other_handle"
        ]

        event_data = Events.objects.filter(id=event_id).values(*fields).first()
        if not event_data:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
        
        event_data["display_handle"] = events_utils.determine_display_handle(event_data)
        
        # Check if user is submitter or admin (optional_jwt sets auth_payload)
        auth_payload = request.auth_payload
        user_id = auth_payload.get("sub") or auth_payload.get("id")
        is_admin = auth_payload.get("role") == "admin"
        
        submission = EventSubmission.objects.filter(created_event_id=event_id).first()
        is_submitter = submission and user_id and str(submission.submitted_by) == str(user_id)
        
        event_data["is_submitter"] = is_submitter
        event_data["screenshot_url"] = submission.screenshot_url if (is_admin or is_submitter) and submission else None
        
        # Get upcoming event dates
        event_data["upcoming_dates"] = list(
            EventDates.objects.filter(event_id=event_id, dtstart_utc__gte=timezone.now())
            .order_by('dtstart_utc').values("dtstart_utc", "dtend_utc")
        )

        return Response(event_data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
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
        threshold = float(request.GET.get("threshold", 0.5))
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
                {"error": "IDs must be a comma-separated list of integers"},
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
        start_date = event.dtstart_utc.strftime("%Y%m%d")
        start_time = event.dtstart_utc.strftime("%H%M%S")
        end_time = event.dtend_utc.strftime("%H%M%S") if event.dtend_utc else start_time

        lines.append("BEGIN:VEVENT")
        lines.append(f"DTSTART:{start_date}T{start_time}Z")
        lines.append(f"DTEND:{start_date}T{end_time}Z")
        lines.append(f"DTSTAMP:{dtstamp}")
        lines.append(f"SUMMARY:{escape_text(event.title)}")

        if event.description:
            lines.append(f"DESCRIPTION:{escape_text(event.description)}")

        if event.location:
            lines.append(f"LOCATION:{escape_text(event.location)}")

        if event.source_url:
            lines.append(f"URL:{event.source_url}")

        lines.append(f"UID:{event.id}@wat2do.com")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


@api_view(["GET"])
@permission_classes([AllowAny])
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
                {"error": "IDs must be a comma-separated list of integers"},
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
            # Format dates for Google Calendar (YYYYMMDDTHHMMSSZ for UTC)
            start_date = event.dtstart_utc.strftime("%Y%m%d")
            start_time = event.dtstart_utc.strftime("%H%M%S")
            end_time = (
                event.dtend_utc.strftime("%H%M%S") if event.dtend_utc else start_time
            )

            start_datetime = f"{start_date}T{start_time}Z"
            end_datetime = f"{start_date}T{end_time}Z"

            # Build details field
            details_parts = []
            if event.description:
                details_parts.append(event.description)
            if event.source_url:
                details_parts.append(event.source_url)
            details = "\n\n".join(details_parts)

            # Build Google Calendar URL
            params = {
                "action": "TEMPLATE",
                "text": event.title,
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


def rss_feed(request):
    """
    Simple RSS feed of upcoming events (returns application/rss+xml).
    """
    now = timezone.now()
    items = Events.objects.filter(dtstart_utc__gte=now).order_by("dtstart_utc")[:50]

    site_url = getattr(settings, "SITE_URL", "https://wat2do.ca")
    rss_items = []
    for ev in items:
        title = escape(ev.title or "Untitled event")
        link = ev.source_url or f"{site_url}/events/{ev.id}"
        description = escape(ev.description or "")
        pub_date = ev.dtstamp.astimezone(timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )
        guid = f"{ev.id}@wat2do"
        enclosure = ""
        if ev.source_image_url:
            enclosure = (
                f'<media:content url="{escape(ev.source_image_url)}" medium="image" />'
            )

        item_xml = f"""
      <item>
        <title>{title}</title>
        <link>{escape(link)}</link>
        <description><![CDATA[{description}]]></description>
        <guid isPermaLink="false">{guid}</guid>
        <pubDate>{pub_date}</pubDate>
        {enclosure}
      </item>
"""
        rss_items.append(item_xml)

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Wat2Do — Upcoming events</title>
    <link>{site_url}</link>
    <atom:link href="{site_url}/rss.xml" rel="self" type="application/rss+xml" />
    <description>Upcoming events at the University of Waterloo</description>
    <lastBuildDate>{timezone.now().astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>
    {''.join(rss_items)}
  </channel>
</rss>"""
    return HttpResponse(rss, content_type="application/rss+xml")


@api_view(["POST"])
@ratelimit(key="ip", rate="10/hr", block=True)
@jwt_required
def extract_event_from_screenshot(request):
    """Extract event data from screenshot without creating event - returns JSON for user to edit"""
    try:
        screenshot = request.FILES.get("screenshot")
        
        if not screenshot:
            return Response(
                {"error": "Screenshot is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Upload to S3
        filename = f"submissions/{uuid.uuid4()}.{screenshot.name.split('.')[-1]}"
        screenshot_url = storage_service.upload_image_data(screenshot.read(), filename)

        if not screenshot_url:
            return Response(
                {"error": "Failed to upload screenshot"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Run OpenAI extraction to get event data
        extracted_list = extract_events_from_caption(
            source_image_url=screenshot_url,
            model="gpt-4o-mini",
        )
        
        if not extracted_list or len(extracted_list) == 0:
            return Response(
                {"error": "Could not extract event data from image. Please ensure the image contains clear event information."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter to only return user-editable fields for the UI
        # This ensures the frontend only shows fields that users should edit
        first_extracted = extracted_list[0] if extracted_list else {}
        allowed_fields = {
            'title', 'dtstart', 'dtend', 'all_day', 'location', 
            'price', 'food', 'registration', 'description'
        }
        
        filtered_data = {
            key: value 
            for key, value in first_extracted.items() 
            if key in allowed_fields
        }
        
        # Ensure all expected fields are present (even if None/empty)
        # This helps the frontend render consistent input fields
        for field in allowed_fields:
            if field not in filtered_data:
                if field == 'all_day':
                    filtered_data[field] = False
                elif field == 'registration':
                    filtered_data[field] = False
                elif field == 'price':
                    filtered_data[field] = None
                else:
                    filtered_data[field] = ""

        # Return first extracted event and the screenshot URL
        return Response({
            "screenshot_url": screenshot_url,
            "extracted_data": filtered_data,
            "all_extracted": extracted_list
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@ratelimit(key="ip", rate="5/hr", block=True)
@jwt_required
def submit_event(request):
    """Submit event for review - accepts screenshot URL and basic event data, computes derived fields automatically"""
    try:
        # Get user info first to validate authentication
        user_info = getattr(request, "auth_payload", {})
        clerk_user_id = user_info.get("sub")
        if not clerk_user_id:
            return Response(
                {"error": "User authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        screenshot_url = request.data.get("screenshot_url")
        extracted_data = request.data.get("extracted_data")

        if not screenshot_url or not extracted_data:
            return Response(
                {"error": "Screenshot URL and extracted data are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate and sanitize user input - CRITICAL SECURITY STEP
        # This prevents mass assignment and injection attacks
        try:
            sanitized_data = validate_and_sanitize_event_data(
                extracted_data, 
                allowed_fields=USER_EDITABLE_FIELDS,
                is_admin=False  # Users are never admin in submit flow
            )
            validate_required_fields(sanitized_data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Compute derived fields (dtstart_utc, dtend_utc, duration, tz, latitude, longitude, source_image_url)
        computed_data = compute_event_fields(sanitized_data, screenshot_url)

        # Filter to only model fields
        allowed_model_fields = {f.name for f in Events._meta.get_fields()}
        cleaned = {
            k: v
            for k, v in computed_data.items()
            if k in allowed_model_fields
            and v is not None
            and not (isinstance(v, str) and v.strip() in {"", '""', "''", '""'})
        }

        # CRITICAL: Force status to PENDING regardless of user input
        # This prevents users from bypassing the approval process
        cleaned["status"] = "PENDING"
        
        # CRITICAL: Force school to University of Waterloo for user submissions
        cleaned["school"] = "University of Waterloo"

        # Use atomic transaction to prevent orphaned records
        with transaction.atomic():
            # Create event
            event = Events.objects.create(**cleaned)
            
            # Set source_url to the event detail page
            source_url = f"https://wat2do.ca/events/{event.id}"
            event.source_url = source_url
            event.save()

            # Create linked submission
            submission = EventSubmission.objects.create(
                screenshot_url=screenshot_url,
                source_url=source_url,
                status="pending",
                submitted_by=clerk_user_id,
                created_event=event,
                extracted_data=[sanitized_data] if sanitized_data else [],
            )

        return Response(
            {
                "id": submission.id, 
                "message": "Event submitted successfully", 
                "event_id": event.id
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@ratelimit(key="ip", rate="100/hr", block=True)
@admin_required
def get_submissions(request):
    try:
        user_info = getattr(request, "auth_payload", {})
        email_from_request = user_info.get("email_addresses", [{}])[0].get("email_address", None)
        
        submissions = EventSubmission.objects.select_related("created_event").all().order_by("-submitted_at")
        data = []
        for s in submissions:
            data.append({
                "id": s.id,
                "screenshot_url": s.screenshot_url,
                "source_url": s.source_url,
                "status": s.status,
                "submitted_by": s.submitted_by,
                "submitted_by_email": email_from_request,
                "submitted_at": s.submitted_at,
                "extracted_data": s.extracted_data,
                "event_id": s.created_event_id,
                "event_title": s.created_event.title if s.created_event else None,
                "admin_notes": s.admin_notes,
            })
        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(["POST"])
@admin_required
@ratelimit(key="ip", rate="100/hr", block=True)
def review_submission(request, submission_id):
    """Approve or reject submission."""
    submission = get_object_or_404(EventSubmission, id=submission_id)
    action = request.data.get("action")
    reviewer_id = getattr(request, "auth_payload", {}).get("sub")

    if action == "approve":
        if not submission.created_event:
            return Response(
                {"error": "No linked event to approve"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get edited extracted_data if provided, otherwise use existing
        edited_data = request.data.get("extracted_data")
        if edited_data:
            # Validate and sanitize admin edits - CRITICAL SECURITY STEP
            try:
                sanitized_data = validate_and_sanitize_event_data(
                    edited_data, 
                    is_admin=True  # Admins can edit additional fields
                )
                validate_required_fields(sanitized_data)
            except ValueError as e:
                return Response(
                    {"error": f"Invalid event data: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Store sanitized data in submission
            submission.extracted_data = sanitized_data
            
            # Update the linked event with sanitized data
            event = submission.created_event
            if event:
                # Compute derived fields from sanitized data
                computed_data = compute_event_fields(
                    sanitized_data, 
                    event.source_image_url
                )
                
                # Get allowed model fields
                allowed_model_fields = {f.name for f in Events._meta.get_fields()}
                
                # Update only the fields present in the sanitized data
                for field, value in computed_data.items():
                    if field in allowed_model_fields and value is not None:
                        # Skip protected fields that shouldn't be manually set
                        if field not in {'id', 'added_at', 'dtstamp'}:
                            setattr(event, field, value)
                
                # When approving, set status to CONFIRMED
                event.status = "CONFIRMED"
                event.save()
        else:
            # No edited data, just approve with existing data
            event = submission.created_event
            event.status = "CONFIRMED"
            event.save()
        
        submission.status = "approved"
        submission.reviewed_at = timezone.now()
        submission.reviewed_by = reviewer_id
        submission.save()
        
        return Response({
            "message": "Event approved", 
            "event_id": submission.created_event.id
        })

    elif action == "reject":
        submission.status = "rejected"
        submission.reviewed_at = timezone.now()
        submission.reviewed_by = reviewer_id
        submission.admin_notes = request.data.get("admin_notes", "")
        submission.save()
        
        # When rejecting, set the linked event status to CANCELLED
        if submission.created_event:
            submission.created_event.status = "CANCELLED"
            submission.created_event.save()
        
        return Response({"message": "Event rejected"})

    return Response(
        {"error": "Invalid action. Use 'approve' or 'reject'"}, 
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET"])
@ratelimit(key="ip", rate="100/hr", block=True)
@jwt_required
def get_user_submissions(request):
    """Get submissions for the authenticated user"""
    try:
        user_id = request.auth_payload.get('sub') or request.auth_payload.get('id')
        user_id_source = 'auth_payload'
        if not user_id:
            logger.warning("events.get_user_submissions: no user_id resolved; returning 401-like response context")
        submissions = EventSubmission.objects.filter(submitted_by=user_id).order_by("-submitted_at")

        count = submissions.count()

        data = [
            {
                "id": s.id,
                "screenshot_url": s.screenshot_url,
                "source_url": s.source_url,
                "status": s.status,
                "submitted_at": s.submitted_at,
                "reviewed_at": s.reviewed_at,
                "admin_notes": s.admin_notes,
                "created_event_id": s.created_event.id if s.created_event else None,
            }
            for s in submissions
        ]

        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@ratelimit(key="ip", rate="30/hr", block=True)
@jwt_required
def delete_submission(request, submission_id): 
    try:
        submission = get_object_or_404(EventSubmission, id=submission_id)

        # Get user ID from auth_payload (set by jwt_required decorator)
        user_info = getattr(request, "auth_payload", {})
        current_user_id = user_info.get('sub') or user_info.get('id')
        
        if not current_user_id:
            return Response(
                {"error": "User authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Compare as strings to avoid type issues
        if str(submission.submitted_by) != str(current_user_id):
            return Response(
                {"error": "Not authorized to delete this submission"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if submission.status == "approved":
            return Response({
                "error": "Approved submissions cannot be removed. Contact support if needed."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete linked event first (cascades to submission)
        event = submission.created_event
        if event:
            event.delete()
            return Response({"message": "Submission and linked event removed"}, status=status.HTTP_200_OK)

        # Fallback: if no linked event, delete submission directly
        submission.delete()
        return Response({"message": "Submission removed"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@ratelimit(key="ip", rate="100/hr", block=True)
@jwt_required
def mark_event_interest(request, event_id):
    """Mark user interest in an event"""
    try:
        event = get_object_or_404(Events, id=event_id)
        user_id = request.auth_payload.get('sub') or request.auth_payload.get('id')
        
        if not user_id:
            return Response({"error": "User authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Create interest if it doesn't exist
        interest, created = EventInterest.objects.get_or_create(
            event=event,
            user_id=user_id
        )
        
        # Get total interest count for this event
        interest_count = EventInterest.objects.filter(event=event).count()
        
        return Response({
            "message": "Interest marked" if created else "Already interested",
            "interested": True,
            "interest_count": interest_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@ratelimit(key="ip", rate="100/hr", block=True)
@jwt_required
def unmark_event_interest(request, event_id):
    """Remove user interest in an event"""
    try:
        event = get_object_or_404(Events, id=event_id)
        user_id = request.auth_payload.get('sub') or request.auth_payload.get('id')
        
        if not user_id:
            return Response({"error": "User authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Delete interest if it exists
        deleted_count, _ = EventInterest.objects.filter(
            event=event,
            user_id=user_id
        ).delete()
        
        # Get total interest count for this event
        interest_count = EventInterest.objects.filter(event=event).count()
        
        return Response({
            "message": "Interest removed" if deleted_count > 0 else "Not interested",
            "interested": False,
            "interest_count": interest_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="100/hr", block=True)
def get_event_interest(request, event_id):
    """Get interest count for an event and whether current user is interested"""
    try:
        event = get_object_or_404(Events, id=event_id)
        
        # Get total interest count
        interest_count = EventInterest.objects.filter(event=event).count()
        
        # Check if current user is interested (if authenticated)
        is_interested = False
        auth_payload = getattr(request, "auth_payload", None)
        if auth_payload:
            user_id = auth_payload.get('sub') or auth_payload.get('id')
            if user_id:
                is_interested = EventInterest.objects.filter(
                    event=event,
                    user_id=user_id
                ).exists()
        
        return Response({
            "event_id": event_id,
            "interest_count": interest_count,
            "is_interested": is_interested
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@ratelimit(key="ip", rate="100/hr", block=True)
@jwt_required
def get_my_interested_event_ids(request):
    """Get list of event IDs that the current user is interested in"""
    try:
        user_id = request.auth_payload.get('sub') or request.auth_payload.get('id')
        
        if not user_id:
            return Response({"error": "User authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get all event IDs the user is interested in
        interested_event_ids = list(
            EventInterest.objects.filter(user_id=user_id).values_list('event_id', flat=True)
        )
        
        return Response({
            "event_ids": interested_event_ids
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="100/hr", block=True)
def get_event_submission(request, event_id):
    """Get submission info for an event"""
    try:
        from django.contrib.auth import authenticate
        
        event = get_object_or_404(Events, id=event_id)
        
        # Try to authenticate the user if JWT token is present (optional authentication)
        user = authenticate(request)
        auth_payload = getattr(request, "auth_payload", None)
        
        # Check if current user is admin
        is_admin = False
        current_user_id = None
        if auth_payload:
            current_user_id = auth_payload.get('sub') or auth_payload.get('id')
            is_admin = auth_payload.get("role") == "admin"
        
        # Try to find the submission for this event
        try:
            submission = EventSubmission.objects.get(created_event=event)
            
            # Check if current user is the submitter
            is_submitter = False
            if current_user_id and submission.submitted_by:
                # Compare as strings to avoid type issues
                is_submitter = str(current_user_id) == str(submission.submitted_by)
                print(f"DEBUG: current_user_id={current_user_id}, submitted_by={submission.submitted_by}, is_submitter={is_submitter}")
            
            return Response({
                "submission_id": submission.id,
                "submitted_by": submission.submitted_by,
                "is_submitter": is_submitter,
                "is_admin": is_admin,
                "status": submission.status,
                "screenshot_url": submission.screenshot_url if (is_submitter or is_admin) else None,
            }, status=status.HTTP_200_OK)
        except EventSubmission.DoesNotExist:
            return Response({
                "submission_id": None,
                "is_submitter": False,
                "is_admin": is_admin,
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
@ratelimit(key="ip", rate="30/hr", block=True)
@jwt_required
def update_event(request, event_id):
    """Update event data (only by submitter or admin)"""
    try:
        event = get_object_or_404(Events, id=event_id)
        
        # Get current user
        user_id = request.auth_payload.get('sub') or request.auth_payload.get('id')
        if not user_id:
            return Response(
                {"error": "User authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is admin or submitter
        is_admin = request.auth_payload.get("role") == "admin"
        is_submitter = False
        
        try:
            submission = EventSubmission.objects.get(created_event=event)
            is_submitter = str(submission.submitted_by) == str(user_id)
        except EventSubmission.DoesNotExist:
            # If no submission exists, only admins can edit
            if not is_admin:
                return Response(
                    {"error": "Event submission not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Check authorization
        if not (is_admin or is_submitter):
            return Response(
                {"error": "Not authorized to edit this event"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the updated event data
        updated_data = request.data.get("event_data")
        if not updated_data or not isinstance(updated_data, dict):
            return Response(
                {"error": "Invalid event data"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate and sanitize input - CRITICAL SECURITY STEP
        try:
            sanitized_data = validate_and_sanitize_event_data(
                updated_data,
                is_admin=is_admin
            )
            validate_required_fields(sanitized_data)
        except ValueError as e:
            return Response(
                {"error": f"Invalid event data: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Compute derived fields
        computed_data = compute_event_fields(
            sanitized_data,
            event.source_image_url
        )
        
        # Get allowed model fields
        allowed_model_fields = {f.name for f in Events._meta.get_fields()}
        
        # Update only safe fields
        for field, value in computed_data.items():
            if field in allowed_model_fields and value is not None:
                # Skip protected fields
                if field not in {'id', 'added_at', 'dtstamp'}:
                    # Non-admins cannot change status
                    if field == 'status' and not is_admin:
                        continue
                    setattr(event, field, value)
        
        event.save()
        
        return Response({
            "message": "Event updated successfully",
            "event_id": event.id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["DELETE"])
@ratelimit(key="ip", rate="30/hr", block=True)
@admin_required
def delete_event(request, event_id):
    """Delete an event and all its related data (admin only)"""
    try:
        event = get_object_or_404(Events, id=event_id)
        
        with transaction.atomic():
            # Delete related EventDates
            deleted_dates_count = EventDates.objects.filter(event=event).delete()[0]
            
            # Delete related EventInterest
            EventInterest.objects.filter(event=event).delete()
            
            # Delete related EventSubmission
            EventSubmission.objects.filter(created_event=event).delete()
            
            # Delete the event itself
            event_title = event.title
            event.delete()
        
        return Response({
            "message": f"Event '{event_title}' and {deleted_dates_count} related dates deleted successfully"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
