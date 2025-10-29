import uuid

from clerk_django.permissions.clerk import ClerkAuthenticated
from django.conf import settings
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

from .models import Events, EventSubmission


@api_view(["GET"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="60/hr", block=True)
def get_events(request):
    """Get all events from database with optional filtering"""
    try:
        search_term = request.GET.get("search", "").strip()

        queryset = Events.objects.filter(status__iexact="CONFIRMED").order_by("dtstart")
        filterset = EventFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(
                {"error": "Invalid filter parameters", "details": filterset.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        filtered_queryset = filterset.qs

        if search_term:
            event_ids = set()

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

            keyword_events = filtered_queryset.filter(or_queries)
            event_ids.update(keyword_events.values_list("id", flat=True))

            # search_embedding = generate_embedding(search_term)
            # dtstart = request.GET.get("dtstart")
            # similar_events = find_similar_events(
            #     embedding=search_embedding, min_date=dtstart
            # )
            # for event in similar_events:
            #     print(event["title"], event["similarity"])
            # similar_event_ids = [event["id"] for event in similar_events]
            # event_ids.update(similar_event_ids)

            if event_ids:
                filtered_queryset = filtered_queryset.filter(id__in=event_ids)
            else:
                filtered_queryset = filtered_queryset.none()

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
        results = list(filtered_queryset.values(*fields))

        for event in results:
            event["display_handle"] = events_utils.determine_display_handle(event)

        return Response(results)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="60/hr", block=True)
def get_event(request, event_id):
    """Get a single event by ID"""
    try:
        event = get_object_or_404(Events, id=event_id)

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
        ]

        event_data = {field: getattr(event, field) for field in fields}
        event_data["display_handle"] = events_utils.determine_display_handle(event_data)

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
@permission_classes([ClerkAuthenticated])
@ratelimit(key="ip", rate="5/hr", block=True)
def submit_event(request):
    """Submit event for review - accepts screenshot file and source URL, runs extraction, creates Event and links submission"""
    try:
        screenshot = request.FILES.get("screenshot")
        source_url = request.data.get("source_url")
        other_handle = request.data.get("other_handle")

        if not screenshot or not source_url:
            return Response(
                {"error": "Screenshot and source URL are required"},
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

        # Run OpenAI extraction to build event data
        event_data = extract_events_from_caption(
            caption_text=f"Event source: {source_url}",
            source_image_url=screenshot_url,
        )

        # Ensure provenance
        if isinstance(event_data, dict):
            event_data["source_url"] = source_url
            event_data["source_image_url"] = event_data.get("source_image_url") or screenshot_url
            if other_handle:
                event_data["other_handle"] = other_handle
        else:
            event_data = {"source_url": source_url, "source_image_url": screenshot_url}
            if other_handle:
                event_data["other_handle"] = other_handle

        # Create Event immediately and link submission
        allowed_fields = {f.name for f in Events._meta.get_fields()}
        cleaned = {
            k: v
            for k, v in (event_data or {}).items()
            if k in allowed_fields
            and not (isinstance(v, str) and v.strip() in {"", "\"\"", "''", "“”"})
        }

        # Basic guard: require at least a title and a start datetime to consider it an event
        if not cleaned.get("title") or not cleaned.get("dtstart"):
            return Response(
                {"error": "Submission does not appear to be an event."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create event with pending status by default
        if "status" not in cleaned or not cleaned.get("status"):
            cleaned["status"] = "PENDING"
        event = Events.objects.create(**cleaned)

        # Attempt to capture submitting user if available (optional for anonymous)
        clerk_user_id = None
        try:
            clerk_user_id = (
                getattr(request, "clerk_user", None) or {}
            ).get("id")
        except Exception:
            clerk_user_id = None

        submission = EventSubmission.objects.create(
            screenshot_url=screenshot_url,
            source_url=source_url,
            status="pending",
            submitted_by=clerk_user_id,
            created_event=event,
            extracted_data=event_data,
        )

        return Response(
            {"id": submission.id, "message": "Event submitted successfully", "event_id": event.id},
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAdminUser])
@ratelimit(key="ip", rate="100/hr", block=True)
def get_submissions(request):
    try:
        submissions = EventSubmission.objects.all().order_by("-submitted_at")
        data = [
            {
                "id": s.id,
                "screenshot_url": s.screenshot_url,
                "source_url": s.source_url,
                "status": s.status,
                "submitted_by": s.submitted_by,
                "submitted_at": s.submitted_at,
                "extracted_data": s.extracted_data,
                "event_id": s.created_event_id,
            }
            for s in submissions
        ]
        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAdminUser])
@ratelimit(key="ip", rate="100/hr", block=True)
def process_submission(request, submission_id):
    """Re-run extraction and update linked Event/extracted_data"""
    try:
        submission = get_object_or_404(EventSubmission, id=submission_id)

        event_data = extract_events_from_caption(
            caption_text=f"Event source: {submission.source_url}",
            source_image_url=submission.screenshot_url,
        )

        if event_data:
            submission.extracted_data = event_data if isinstance(event_data, dict) else {}
            submission.save()

            # Update linked event with fresh data (only known fields)
            event = submission.created_event
            if event and isinstance(event_data, dict):
                for field in [f.name for f in Events._meta.get_fields()]:
                    if field in event_data:
                        setattr(event, field, event_data[field])
                event.save()

            return Response(
                {"id": submission.id, "extracted_data": submission.extracted_data, "event_id": submission.created_event_id}
            )

        return Response(
            {"error": "Failed to extract event data"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAdminUser])
@ratelimit(key="ip", rate="100/hr", block=True)
def review_submission(request, submission_id):
    """Approve, reject, or edit submission"""
    try:
        submission = get_object_or_404(EventSubmission, id=submission_id)
        action = request.data.get("action")  # 'approve', 'reject', 'edit'

        if action == "approve":
            # Ensure event exists (it should from submission time)
            event = submission.created_event
            if not event:
                return Response({"error": "No linked event to approve"}, status=status.HTTP_400_BAD_REQUEST)

            submission.status = "approved"
            submission.reviewed_at = timezone.now()
            submission.reviewed_by = request.clerk_user.get('email_addresses', [{}])[0].get('email_address')
            submission.save()

            return Response(
                {"message": "Event approved", "event_id": event.id}
            )

        elif action == "reject":
            submission.status = "rejected"
            submission.reviewed_at = timezone.now()
            submission.reviewed_by = request.clerk_user.get('email_addresses', [{}])[0].get('email_address')
            submission.admin_notes = request.data.get("notes", "")
            submission.save()

            return Response({"message": "Event rejected"})

        elif action == "edit":
            # Update event data and extracted_data
            event_data = request.data.get("event_data") or {}
            submission.extracted_data = event_data
            submission.save()

            event = submission.created_event
            if event and isinstance(event_data, dict):
                for field in [f.name for f in Events._meta.get_fields()]:
                    if field in event_data:
                        setattr(event, field, event_data[field])
                event.save()

            return Response({"message": "Event data updated"})

        return Response(
            {"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([ClerkAuthenticated])
@ratelimit(key="ip", rate="100/hr", block=True)
def get_user_submissions(request):
    """Get submissions for the authenticated user"""
    try:
        submissions = EventSubmission.objects.filter(submitted_by=request.clerk_user.get('id')).order_by("-submitted_at")

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
@permission_classes([ClerkAuthenticated])
@ratelimit(key="ip", rate="30/hr", block=True)
def delete_submission(request, submission_id): 
    try:
        submission = get_object_or_404(EventSubmission, id=submission_id)

        current_user_id = (getattr(request, "clerk_user", None) or {}).get("id")
        if not current_user_id or submission.submitted_by != current_user_id:
            return Response({"error": "Not authorized to delete this submission"}, status=status.HTTP_403_FORBIDDEN)

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
