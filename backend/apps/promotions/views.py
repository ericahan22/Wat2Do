from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.auth import admin_required
from apps.events.models import Events

from .models import EventPromotion


@api_view(["POST"])
@admin_required
def promote_event(request, event_id):
    """
    Promote an event by creating an EventPromotion record.

    POST /api/promotions/events/<event_id>/promote/
    """
    try:
        event = Events.objects.get(id=event_id)
    except Events.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    if hasattr(event, "promotion"):
        return Response(
            {"error": "Event is already promoted. Use PATCH to update."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    priority = request.data.get("priority", 1)
    expires_at = request.data.get("expires_at")
    promoted_by = request.data.get("promoted_by", request.user.username)
    promotion_type = request.data.get("promotion_type", "standard")
    notes = request.data.get("notes", "")

    # Validate input data
    validation_error = _validate_promotion_data(priority, promotion_type, expires_at)
    if validation_error:
        return validation_error

    # Parse expires_at if provided
    expires_at_dt = None
    if expires_at:
        expires_at_dt = _parse_expires_at(expires_at)
        if isinstance(expires_at_dt, Response):  # Error response
            return expires_at_dt

    promotion = EventPromotion.objects.create(
        event=event,
        is_active=True,
        promoted_by=promoted_by,
        expires_at=expires_at_dt,
        priority=priority,
        promotion_type=promotion_type,
        notes=notes,
    )

    return Response(
        {
            "message": "Event promoted successfully",
            "event_id": event.id,
            "promotion": {
                "is_active": promotion.is_active,
                "promoted_at": promotion.promoted_at.isoformat(),
                "promoted_by": promotion.promoted_by,
                "expires_at": promotion.expires_at.isoformat()
                if promotion.expires_at
                else None,
                "priority": promotion.priority,
                "promotion_type": promotion.promotion_type,
                "notes": promotion.notes,
            },
        },
        status=status.HTTP_201_CREATED,
    )


def _validate_promotion_data(priority, promotion_type, expires_at):
    """Validate promotion data and return error response if invalid."""
    # Validate priority
    if not isinstance(priority, int) or priority < 1 or priority > 10:
        return Response(
            {"error": "Priority must be an integer between 1 and 10"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate promotion type
    valid_types = ["standard", "featured", "urgent", "sponsored"]
    if promotion_type not in valid_types:
        return Response(
            {
                "error": f"Invalid promotion_type. Must be one of: {', '.join(valid_types)}"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None


def _parse_expires_at(expires_at):
    """Parse expires_at string and return datetime or error response."""
    try:
        from dateutil import parser

        expires_at_dt = parser.isoparse(expires_at)

        # Check if in future
        if expires_at_dt < timezone.now():
            return Response(
                {"error": "Expiration date must be in the future"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return expires_at_dt
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid expires_at format. Use ISO-8601 format."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@admin_required
def unpromote_event(request, event_id):
    """
    Deactivate an event promotion.

    POST /api/promotions/events/<event_id>/unpromote/
    """
    try:
        promotion = EventPromotion.objects.get(event_id=event_id)
    except EventPromotion.DoesNotExist:
        return Response(
            {"error": "Event is not currently promoted"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not promotion.is_active:
        return Response(
            {"error": "Event promotion is already inactive"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    promotion.is_active = False
    promotion.save()

    return Response(
        {
            "message": "Event unpromoted successfully",
            "event_id": event_id,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_promoted_events(request):
    """
    Get all currently promoted events (active, non-expired).

    GET /api/promotions/events/promoted/
    """
    try:
        from django.db.models import Q

        promotion_type_filter = request.GET.get("promotion_type")

        # Get active promotions
        promotions = (
            EventPromotion.objects.filter(is_active=True)
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
            .select_related("event")
            .order_by("-priority", "-promoted_at")
        )

        # Filter by promotion type if provided
        if promotion_type_filter:
            promotions = promotions.filter(promotion_type=promotion_type_filter)

        # Build response
        events_data = []
        for promotion in promotions:
            event = promotion.event
            events_data.append(
                {
                    "id": event.id,
                    "title": event.title,
                    "dtstart": event.dtstart_utc.isoformat(),
                    "dtend": event.dtend_utc.isoformat() if event.dtend_utc else None,
                    "location": event.location,
                    "description": event.description,
                    "source_image_url": event.source_image_url,
                    "club_handle": event.ig_handle
                    or event.discord_handle
                    or event.x_handle
                    or event.tiktok_handle
                    or event.fb_handle
                    or event.school,
                    "promotion": {
                        "is_active": promotion.is_active,
                        "promoted_at": promotion.promoted_at.isoformat(),
                        "priority": promotion.priority,
                        "promotion_type": promotion.promotion_type,
                        "expires_at": promotion.expires_at.isoformat()
                        if promotion.expires_at
                        else None,
                    },
                }
            )

        return Response({"promoted_events": events_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": f"Failed to fetch promoted events: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@admin_required
def get_promotion_status(request, event_id):
    """
    Get promotion status for a specific event.

    GET /api/promotions/events/<event_id>/promotion-status/
    """
    try:
        event = Events.objects.get(id=event_id)
    except Events.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if event has promotion
    if not hasattr(event, "promotion"):
        return Response(
            {
                "event_id": event.id,
                "event_name": event.name,
                "is_promoted": False,
                "promotion": None,
            },
            status=status.HTTP_200_OK,
        )

    promotion = event.promotion

    return Response(
        {
            "event_id": event.id,
            "event_name": event.name,
            "is_promoted": promotion.is_active,
            "promotion": {
                "is_active": promotion.is_active,
                "promoted_at": promotion.promoted_at.isoformat(),
                "promoted_by": promotion.promoted_by,
                "expires_at": promotion.expires_at.isoformat()
                if promotion.expires_at
                else None,
                "priority": promotion.priority,
                "promotion_type": promotion.promotion_type,
                "notes": promotion.notes,
                "is_expired": promotion.is_expired,
            },
        },
        status=status.HTTP_200_OK,
    )
