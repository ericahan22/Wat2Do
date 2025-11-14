import json
import uuid
from datetime import timedelta

import pytz
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.html import escape
from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.auth import admin_required, jwt_required, optional_jwt
from services.openai_service import extract_events_from_caption
from services.storage_service import storage_service
from utils import events_utils
from utils.date_utils import parse_utc_datetime
from utils.filters import EventFilter
from utils.validation import validate_event_data

from .models import EventDates, EventInterest, Events, EventSubmission


@api_view(["GET"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="600/hr", block=True)
def get_events(request):
    """Get events with cursor-based pagination for infinite scroll"""
    try:
        from django.db.models import Min, Prefetch

        search_term = request.GET.get("search", "").strip()
        dtstart_utc_param = request.GET.get("dtstart_utc", "").strip()
        cursor = request.GET.get("cursor", "").strip()
        limit = 20
        all_events = request.GET.get("all", "").lower() == "true"

        # Start with Events queryset
        events_queryset = Events.objects.filter(
            status="CONFIRMED", school="University of Waterloo"
        )

        # Apply default upcoming events filter using EventDates join
        if not dtstart_utc_param:
            now = timezone.now()
            ninety_minutes_ago = now - timedelta(minutes=90)
            # Filter events that have at least one upcoming date
            events_queryset = events_queryset.filter(
                event_dates__dtstart_utc__gte=ninety_minutes_ago
            ).distinct()

        filterset = EventFilter(request.GET, queryset=events_queryset)
        if not filterset.is_valid():
            return Response(
                {"message": "Invalid filter parameters", "details": filterset.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        filtered_queryset = filterset.qs.distinct()

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

        # Get events with their earliest date for ordering and cursor
        # Annotate with earliest dtstart_utc
        filtered_queryset = filtered_queryset.annotate(
            earliest_dtstart=Min("event_dates__dtstart_utc")
        ).order_by("earliest_dtstart", "id")

        # Handle cursor-based pagination
        if cursor and not all_events:
            # Cursor format: "{dtstart_utc_iso}_{event_id}"
            try:
                cursor_parts = cursor.split("_")
                cursor_dtstart_utc_str = cursor_parts[0]
                cursor_id = int(cursor_parts[1])

                cursor_dtstart_utc = parse_utc_datetime(cursor_dtstart_utc_str)

                # Filter events after cursor position
                filtered_queryset = filtered_queryset.filter(
                    Q(earliest_dtstart__gt=cursor_dtstart_utc)
                    | (Q(earliest_dtstart=cursor_dtstart_utc) & Q(id__gt=cursor_id))
                )
            except (ValueError, IndexError):
                return Response(
                    {"message": "Invalid cursor format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get total count for the filtered queryset
        total_count = filtered_queryset.count()

        # Fetch events with prefetched dates
        if all_events:
            events_list = list(
                filtered_queryset.prefetch_related(
                    Prefetch(
                        "event_dates",
                        queryset=EventDates.objects.order_by("dtstart_utc"),
                    )
                )
            )
        else:
            events_list = list(
                filtered_queryset.prefetch_related(
                    Prefetch(
                        "event_dates",
                        queryset=EventDates.objects.order_by("dtstart_utc"),
                    )
                )[: limit + 1]
            )

        # Build results with most recent upcoming occurrence dates
        results = []
        now = timezone.now()
        ninety_minutes_ago = now - timedelta(minutes=90)

        for event in events_list:
            # Get all event dates and filter for upcoming ones
            all_dates = list(event.event_dates.all())
            # Filter to only upcoming dates (>= ninety_minutes_ago to match the filter logic)
            upcoming_dates = [
                date for date in all_dates if date.dtstart_utc >= ninety_minutes_ago
            ]
            # Select the most recent upcoming date (first one since they're ordered by dtstart_utc)
            # If no upcoming dates, fall back to the earliest date overall
            selected_date = (
                upcoming_dates[0]
                if upcoming_dates
                else (all_dates[0] if all_dates else None)
            )

            event_data = {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "location": event.location,
                "dtstart_utc": selected_date.dtstart_utc if selected_date else None,
                "dtend_utc": selected_date.dtend_utc if selected_date else None,
                "price": event.price,
                "food": event.food,
                "registration": event.registration,
                "source_image_url": event.source_image_url,
                "club_type": event.club_type,
                "added_at": event.added_at,
                "school": event.school,
                "source_url": event.source_url,
                "ig_handle": event.ig_handle,
                "discord_handle": event.discord_handle,
                "x_handle": event.x_handle,
                "tiktok_handle": event.tiktok_handle,
                "fb_handle": event.fb_handle,
                "other_handle": event.other_handle,
            }
            event_data["display_handle"] = events_utils.determine_display_handle(
                event_data
            )
            results.append(event_data)

        # Determine if there's a next page
        if all_events:
            next_cursor = None
        else:
            has_more = len(results) > limit
            if has_more:
                results = results[:limit]  # Remove the extra item

                # Generate next cursor from last item
                last_event = results[-1]
                if last_event.get("dtstart_utc"):
                    next_cursor = (
                        f"{last_event['dtstart_utc'].isoformat()}_{last_event['id']}"
                    )
                else:
                    next_cursor = None
            else:
                next_cursor = None

        return Response(
            {
                "results": results,
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "totalCount": total_count,
            }
        )

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([AllowAny])
@optional_jwt
@ratelimit(key="ip", rate="60/hr", block=True)
def get_event(request, event_id):
    """Get a single event by ID with dates"""
    try:
        event = Events.objects.get(id=event_id)

        # Convert model instance to dictionary
        event_data = model_to_dict(event)

        event_data["display_handle"] = events_utils.determine_display_handle(event)

        submission = EventSubmission.objects.filter(created_event_id=event_id).first()

        event_data["is_submitter"] = (
            submission
            and request.user_id
            and str(submission.submitted_by) == str(request.user_id)
        )

        # Get all event dates
        event_data["occurrences"] = list(
            EventDates.objects.filter(event_id=event_id)
            .order_by("dtstart_utc")
            .values("dtstart_utc", "dtend_utc")
        )

        return Response(event_data)

    except Events.DoesNotExist:
        return Response(
            {"message": "Event not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
                {"message": "Missing required query parameter: ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse ids
        try:
            id_list = [int(x) for x in ids_param.split(",") if x]
        except ValueError:
            return Response(
                {"message": "IDs must be a comma-separated list of integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        events = Events.objects.filter(id__in=id_list)

        if not events.exists():
            return Response(
                {"message": "No events found with the provided IDs"},
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
            {"message": f"Failed to export events: {e!s}"},
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

    # Prefetch event dates
    events_with_dates = events.prefetch_related("event_dates")

    for event in events_with_dates:
        # Get all dates for this event
        event_dates = list(event.event_dates.all().order_by("dtstart_utc"))

        if not event_dates:
            # Skip events with no dates
            continue

        # Create a VEVENT for each occurrence
        for date_obj in event_dates:
            start_date = date_obj.dtstart_utc.strftime("%Y%m%d")
            start_time = date_obj.dtstart_utc.strftime("%H%M%S")
            end_time = (
                date_obj.dtend_utc.strftime("%H%M%S")
                if date_obj.dtend_utc
                else start_time
            )

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

            lines.append(f"UID:{event.id}-{date_obj.id}@wat2do.com")
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
                {"message": "Missing required query parameter: ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse ids
        try:
            id_list = [int(x) for x in ids_param.split(",") if x]
        except ValueError:
            return Response(
                {"message": "IDs must be a comma-separated list of integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(id_list) == 0:
            return Response(
                {"message": "No valid event IDs provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch events with dates
        events = Events.objects.filter(id__in=id_list).prefetch_related("event_dates")

        if not events.exists():
            return Response(
                {"message": "No events found with the provided IDs"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Generate Google Calendar URLs (one per occurrence)
        urls = []
        from urllib.parse import urlencode

        for event in events:
            # Get all dates for this event, ordered by start time
            event_dates = list(event.event_dates.all().order_by("dtstart_utc"))

            if not event_dates:
                # Skip events with no dates
                continue

            # Create a URL for each occurrence (or just the first one)
            # For simplicity, we'll use the earliest occurrence
            date_obj = event_dates[0]

            # Format dates for Google Calendar (YYYYMMDDTHHMMSSZ for UTC)
            start_date = date_obj.dtstart_utc.strftime("%Y%m%d")
            start_time = date_obj.dtstart_utc.strftime("%H%M%S")
            end_time = (
                date_obj.dtend_utc.strftime("%H%M%S")
                if date_obj.dtend_utc
                else start_time
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
            {"message": f"Failed to generate Google Calendar URLs: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def rss_feed(request):
    """
    Simple RSS feed of upcoming events (returns application/rss+xml).
    """
    from django.db.models import Min

    now = timezone.now()
    # Filter events that have at least one upcoming date
    items = (
        Events.objects.filter(event_dates__dtstart_utc__gte=now, status="CONFIRMED")
        .annotate(earliest_dtstart=Min("event_dates__dtstart_utc"))
        .order_by("earliest_dtstart")[:50]
        .prefetch_related("event_dates")
    )

    site_url = getattr(settings, "SITE_URL", "https://wat2do.ca")
    rss_items = []
    for ev in items:
        # Get earliest date for pub_date
        event_dates = list(ev.event_dates.all().order_by("dtstart_utc"))
        earliest_date = event_dates[0] if event_dates else None

        title = escape(ev.title or "Untitled event")
        link = ev.source_url or f"{site_url}/events/{ev.id}"
        description = escape(ev.description or "")

        # Use earliest date or added_at as fallback
        if earliest_date:
            pub_date = earliest_date.dtstart_utc.astimezone(pytz.UTC).strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            )
        elif ev.added_at:
            pub_date = ev.added_at.astimezone(pytz.UTC).strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            )
        else:
            pub_date = (
                timezone.now()
                .astimezone(pytz.UTC)
                .strftime("%a, %d %b %Y %H:%M:%S GMT")
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
                {"message": "Screenshot is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Upload to S3
        filename = f"submissions/{uuid.uuid4()}.{screenshot.name.split('.')[-1]}"
        source_image_url = storage_service.upload_image_data(
            screenshot.read(), filename
        )

        if not source_image_url:
            return Response(
                {"message": "Failed to upload image"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        extracted_list = extract_events_from_caption(
            source_image_url=source_image_url,
            model="gpt-4o-mini",
        )

        if not extracted_list or len(extracted_list) == 0:
            return Response(
                {
                    "message": "Could not extract event data from image. Please ensure the image contains clear event information."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return user-editable fields with occurrences (flat structure)
        first_extracted = extracted_list[0] if extracted_list else {}
        event_data = {
            "title": first_extracted.get("title", ""),
            "description": first_extracted.get("description", ""),
            "location": first_extracted.get("location", ""),
            "price": first_extracted.get("price"),
            "food": first_extracted.get("food", ""),
            "registration": first_extracted.get("registration", False),
            "occurrences": first_extracted.get("occurrences", []),
        }

        # Return event data with source_image_url (flat structure)
        return Response(
            {
                "source_image_url": source_image_url,
                **event_data,
                "all_extracted": extracted_list,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@ratelimit(key="ip", rate="5/hr", block=True)
@jwt_required
def submit_event(request):
    """Submit event for review"""
    try:
        data = json.loads(request.body)
        source_image_url = data.get("source_image_url")

        if not source_image_url:
            return Response(
                {"message": "Source image URL is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Event data is passed flat at top level
        cleaned = validate_event_data(data)

        with transaction.atomic():
            event = Events.objects.create(
                title=cleaned["title"],
                description=cleaned.get("description"),
                location=cleaned["location"],
                source_image_url=source_image_url,
                food=cleaned.get("food"),
                price=cleaned.get("price"),
                registration=cleaned.get("registration", False),
                status="PENDING",
                school="University of Waterloo",
            )
            event.source_url = f"https://wat2do.ca/events/{event.id}"
            event.save()

            # Create EventDates for each occurrence
            for occ in cleaned["occurrences"]:
                dtstart_utc = parse_utc_datetime(occ["dtstart_utc"])
                dtend_utc = (
                    parse_utc_datetime(occ.get("dtend_utc"))
                    if occ.get("dtend_utc")
                    else None
                )

                EventDates.objects.create(
                    event=event,
                    dtstart_utc=dtstart_utc,
                    dtend_utc=dtend_utc,
                    duration=dtend_utc - dtstart_utc if dtend_utc else None,
                    tz=occ.get("tz", "America/Toronto"),
                )

            EventSubmission.objects.create(
                submitted_by=request.user_id,
                created_event=event,
            )

        return Response(
            {"message": "Event submitted successfully"}, status=status.HTTP_201_CREATED
        )
    except ValueError as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@ratelimit(key="ip", rate="100/hr", block=True)
@admin_required
def get_submissions(request):
    try:
        submissions = (
            EventSubmission.objects.select_related("created_event")
            .all()
            .order_by("-submitted_at")
        )
        data = [
            {
                "id": s.id,
                "source_image_url": s.created_event.source_image_url
                if s.created_event
                else None,
                "status": "approved"
                if s.reviewed_at and s.created_event.status == "CONFIRMED"
                else "rejected"
                if s.reviewed_at
                else "pending",
                "submitted_at": s.submitted_at,
                "submitted_by": s.submitted_by,
                "event_title": s.created_event.title if s.created_event else None,
                "event_id": s.created_event_id,
            }
            for s in submissions
        ]
        return Response(data)
    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@admin_required
@ratelimit(key="ip", rate="100/hr", block=True)
def review_submission(request, event_id):
    """Approve or reject submission"""
    try:
        data = json.loads(request.body)
        event = get_object_or_404(Events, id=event_id)
        submission = EventSubmission.objects.filter(created_event=event).first()
        if not submission:
            return Response(
                {"message": "No submission found for this event"},
                status=status.HTTP_404_NOT_FOUND,
            )
        action = data.get("action")

        if action == "approve":
            event.status = "CONFIRMED"
            event.save()
            submission.reviewed_at = timezone.now()
            submission.reviewed_by = request.user_id
            submission.save()
            return Response({"message": "Event approved", "event_id": event.id})

        elif action == "reject":
            submission.reviewed_at = timezone.now()
            submission.reviewed_by = request.user_id
            submission.save()
            if event:
                event.status = "CANCELLED"
                event.save()
            return Response({"message": "Event rejected"})

        return Response(
            {"message": "Invalid action. Use 'approve' or 'reject'"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@ratelimit(key="ip", rate="100/hr", block=True)
@jwt_required
def get_user_submissions(request):
    """Get submissions for the authenticated user"""
    try:
        submissions = (
            EventSubmission.objects.filter(submitted_by=request.user_id)
            .select_related("created_event")
            .order_by("-submitted_at")
        )
        data = [
            {
                "id": s.id,
                "source_image_url": s.created_event.source_image_url
                if s.created_event
                else None,
                "status": "approved"
                if s.reviewed_at and s.created_event.status == "CONFIRMED"
                else "rejected"
                if s.reviewed_at
                else "pending",
                "submitted_at": s.submitted_at,
                "reviewed_at": s.reviewed_at,
                "event_id": s.created_event_id,
                "event_title": s.created_event.title if s.created_event else None,
            }
            for s in submissions
        ]
        return Response(data)
    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["DELETE"])
@ratelimit(key="ip", rate="30/hr", block=True)
@jwt_required
def delete_submission(request, event_id):
    try:
        event = get_object_or_404(Events, id=event_id)
        submission = event.submission

        if event.status == "CONFIRMED":
            return Response(
                {
                    "message": "Approved submissions cannot be removed. Contact support if needed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete linked event first (cascades to submission)
        event = submission.created_event
        if event:
            event.delete()
            return Response(
                {"message": "Submission and linked event removed"},
                status=status.HTTP_200_OK,
            )

        submission.delete()
        return Response({"message": "Submission removed"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@ratelimit(key="ip", rate="100/hr", block=True)
@jwt_required
def mark_event_interest(request, event_id):
    """Mark user interest in an event"""
    try:
        event = get_object_or_404(Events, id=event_id)

        # Create interest if it doesn't exist
        interest, created = EventInterest.objects.get_or_create(
            event=event, user_id=request.user_id
        )

        # Get total interest count for this event
        interest_count = EventInterest.objects.filter(event=event).count()

        return Response(
            {
                "message": "Interest marked" if created else "Already interested",
                "interested": True,
                "interest_count": interest_count,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["DELETE"])
@ratelimit(key="ip", rate="100/hr", block=True)
@jwt_required
def unmark_event_interest(request, event_id):
    """Remove user interest in an event"""
    try:
        event = get_object_or_404(Events, id=event_id)

        deleted_count, _ = EventInterest.objects.filter(
            event=event, user_id=request.user_id
        ).delete()

        # Get total interest count for this event
        interest_count = EventInterest.objects.filter(event=event).count()

        return Response(
            {
                "message": "Interest removed"
                if deleted_count > 0
                else "Not interested",
                "interested": False,
                "interest_count": interest_count,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@ratelimit(key="ip", rate="100/hr", block=True)
@jwt_required
def get_my_interested_event_ids(request):
    """Get list of event IDs that the current user is interested in"""
    try:
        user_id = request.user_id

        # Get all event IDs the user is interested in
        interested_event_ids = list(
            EventInterest.objects.filter(user_id=user_id).values_list(
                "event_id", flat=True
            )
        )

        return Response({"event_ids": interested_event_ids}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["PUT"])
@ratelimit(key="ip", rate="30/hr", block=True)
@jwt_required
def update_event(request, event_id):
    """Update event data (only by submitter or admin)"""
    try:
        event = get_object_or_404(Events, id=event_id)

        # Check if user is submitter
        is_submitter = False

        try:
            submission = EventSubmission.objects.get(created_event=event)
            is_submitter = str(submission.submitted_by) == str(request.user_id)
        except EventSubmission.DoesNotExist:
            # If no submission exists, only admins can edit
            if not request.is_admin:
                return Response(
                    {"message": "Event submission not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Check authorization
        if not (request.is_admin or is_submitter):
            return Response(
                {"message": "Not authorized to edit this event"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the updated event data
        updated_data = request.data.get("event_data")
        if not updated_data or not isinstance(updated_data, dict):
            return Response(
                {"message": "Invalid event data"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate and sanitize input
        try:
            cleaned = validate_event_data(updated_data)
        except ValueError as e:
            return Response(
                {"message": f"Invalid event data: {e!s}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update event fields
        if cleaned.get("title"):
            event.title = cleaned["title"]
        if cleaned.get("location"):
            event.location = cleaned["location"]
        if cleaned.get("description"):
            event.description = cleaned["description"]
        if cleaned.get("food"):
            event.food = cleaned["food"]
        if cleaned.get("price") is not None:
            event.price = cleaned["price"]
        if "registration" in cleaned:
            event.registration = cleaned["registration"]
        if "source_url" in cleaned:
            event.source_url = cleaned.get("source_url")

        # Update occurrences if provided
        if cleaned.get("occurrences"):
            EventDates.objects.filter(event=event).delete()
            for occ in cleaned["occurrences"]:
                dtstart_utc = parse_utc_datetime(occ["dtstart_utc"])
                dtend_utc = (
                    parse_utc_datetime(occ.get("dtend_utc"))
                    if occ.get("dtend_utc")
                    else None
                )

                EventDates.objects.create(
                    event=event,
                    dtstart_utc=dtstart_utc,
                    dtend_utc=dtend_utc,
                    duration=dtend_utc - dtstart_utc if dtend_utc else None,
                    tz=occ.get("tz", "America/Toronto"),
                )

        event.save()

        return Response(
            {"message": "Event updated successfully", "event_id": event.id},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

        return Response(
            {
                "message": f"Event '{event_title}' and {deleted_dates_count} related dates deleted successfully"
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Boost event


@api_view(["POST", "GET"])
@jwt_required
def boost_event_view(request, event_id):
    """
    Boost an event by creating/updating an EventPromotion.
    Body/query should include 'days' (int).
    Example: POST /events/123/boost?days=7
    """
    if not request.user_id:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    # Parse and validate integer days from query/body
    days_str = request.GET.get("days") or request.data.get("days")
    if not days_str:
        return Response(
            {"error": "Missing 'days' parameter"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        days = int(days_str)
    except (TypeError, ValueError):
        return Response(
            {"error": "Invalid 'days' parameter: must be an integer"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if days <= 0:
        return Response(
            {"error": "Days must be a positive integer"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get the event
    event = get_object_or_404(Events, pk=event_id)

    # Check if user is the owner (through EventSubmission)
    is_owner = False
    try:
        submission = EventSubmission.objects.get(created_event=event)
        is_owner = str(submission.submitted_by) == str(request.user_id)
    except EventSubmission.DoesNotExist:
        pass

    # Only owner or admin can boost
    if not (is_owner or request.is_admin):
        return Response(
            {"error": "You can only boost your own events"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Create or update promotion
    from django.utils import timezone

    from apps.promotions.models import EventPromotion

    expires_at = timezone.now() + timedelta(days=days)

    promotion, created = EventPromotion.objects.update_or_create(
        event=event,
        defaults={
            "is_active": True,
            "expires_at": expires_at,
            "promoted_by": request.user_id or "unknown",
            "priority": 5,  # Default priority
            "promotion_type": "standard",
        },
    )

    return Response(
        {
            "ok": True,
            "promotion": {
                "starts_at": promotion.promoted_at.isoformat(),
                "ends_at": promotion.expires_at.isoformat()
                if promotion.expires_at
                else None,
                "active": promotion.is_active,
            },
        },
        status=status.HTTP_200_OK,
    )
