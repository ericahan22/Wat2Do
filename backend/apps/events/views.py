from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import escape
from django.shortcuts import get_object_or_404
from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from services.openai_service import generate_embedding
from utils import events_utils
from utils.embedding_utils import find_similar_events
from utils.filters import EventFilter

from .models import Events


@api_view(["GET"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="60/hr", block=True)
def get_events(request):
    """Get all events from database with optional filtering"""
    try:
        search_term = request.GET.get("search", "").strip()

        # Start with base queryset, ordered by dtstart
        queryset = Events.objects.all().order_by("dtstart")

        # Apply standard filters (dates, price, club_type, etc.)
        filterset = EventFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(
                {"error": "Invalid filter parameters", "details": filterset.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        filtered_queryset = filterset.qs

        # Apply both keyword and semantic search if search term provided
        if search_term:
            event_ids = set()
            
            keyword_events = filtered_queryset.filter(
                Q(title__icontains=search_term) |
                Q(location__icontains=search_term)
            )
            event_ids.update(keyword_events.values_list('id', flat=True))

            # Apply vector similarity search
            search_embedding = generate_embedding(search_term)
            dtstart = request.GET.get("dtstart")
            similar_events = find_similar_events(
                embedding=search_embedding, min_date=dtstart
            )
            for event in similar_events:
                print(event["title"], event["similarity"])
            similar_event_ids = [event["id"] for event in similar_events]
            event_ids.update(similar_event_ids)

            # Filter by combined results
            if event_ids:
                filtered_queryset = filtered_queryset.filter(id__in=event_ids)

        # Return selected event fields
        fields = [
            "id",
            "title",
            "description",
            "location",
            "dtstart",
            "dtend",
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
        results = list(filtered_queryset.values(*fields))

        # Add display_handle field to each event
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
        
        # Return selected event fields (same as get_events)
        fields = [
            "id",
            "title",
            "description",
            "location",
            "dtstart",
            "dtend",
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
        threshold = float(request.GET.get("threshold", 0.3))
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
        start_date = event.dtstart.strftime("%Y%m%d")
        start_time = event.dtstart.strftime("%H%M%S")
        end_time = event.dtend.strftime("%H%M%S") if event.dtend else start_time

        lines.append("BEGIN:VEVENT")
        lines.append(f"DTSTART:{start_date}T{start_time}")
        lines.append(f"DTEND:{start_date}T{end_time}")
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
            start_date = event.dtstart.strftime("%Y%m%d")
            start_time = event.dtstart.strftime("%H%M%S")
            end_time = event.dtend.strftime("%H%M%S") if event.dtend else start_time

            start_datetime = f"{start_date}T{start_time}"
            end_datetime = f"{start_date}T{end_time}"

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
    items = Events.objects.filter(dtstart__gte=now).order_by("dtstart")[:50]

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
