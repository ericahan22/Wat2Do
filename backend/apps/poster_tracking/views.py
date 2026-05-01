from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.auth import admin_required

from .models import PosterCampaign, PosterScan


def _poster_payload(poster, base_url=None):
    scan_url = _build_scan_url(poster.id, base_url)
    return {
        "id": str(poster.id),
        "label": poster.label,
        "destination_url": poster.destination_url,
        "scan_count": poster.scan_count,
        "needs_location": not poster.has_first_location,
        "first_location": {
            "latitude": float(poster.first_scan_latitude)
            if poster.first_scan_latitude is not None
            else None,
            "longitude": float(poster.first_scan_longitude)
            if poster.first_scan_longitude is not None
            else None,
            "accuracy_m": poster.first_scan_accuracy_m,
            "captured_at": poster.first_scan_at.isoformat()
            if poster.first_scan_at
            else None,
        },
        "scan_url": scan_url,
        "qr_svg": _qr_svg(scan_url),
        "created_at": poster.created_at.isoformat(),
    }


def _scan_payload(scan):
    return {
        "id": scan.id,
        "poster_id": str(scan.poster_id),
        "scan_number": scan.scan_number,
        "created_at": scan.created_at.isoformat(),
        "user_agent": scan.user_agent,
    }


def _build_scan_url(poster_id, base_url=None):
    root = (base_url or _default_frontend_base_url()).rstrip("/") + "/"
    return urljoin(root, f"poster/{poster_id}")


def _default_frontend_base_url():
    return getattr(settings, "FRONTEND_URL", "https://wat2do.ca")


def _default_destination_url():
    return urljoin(_default_frontend_base_url().rstrip("/") + "/", "events")


def _qr_svg(url):
    factory = qrcode.image.svg.SvgPathImage
    image = qrcode.make(url, image_factory=factory)
    return image.to_string(encoding="unicode")


def _parse_coordinate(value, minimum, maximum):
    if value in (None, ""):
        return None
    try:
        coordinate = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("Coordinates must be numbers") from exc
    if coordinate < Decimal(str(minimum)) or coordinate > Decimal(str(maximum)):
        raise ValueError(f"Coordinate must be between {minimum} and {maximum}")
    return coordinate.quantize(Decimal("0.000001"))


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _parse_accuracy(value):
    if value in ("", None):
        return None
    try:
        accuracy = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("accuracy_m must be a number") from exc
    return accuracy if accuracy >= 0 else None


def _record_scan_for_poster(
    poster, request, latitude=None, longitude=None, accuracy=None
):
    should_store_location = (
        not poster.has_first_location and latitude is not None and longitude is not None
    )
    scan_number = poster.scan_count + 1

    PosterScan.objects.create(
        poster=poster,
        scan_number=scan_number,
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        ip_address=_client_ip(request),
        referrer=request.META.get("HTTP_REFERER", ""),
    )

    poster.scan_count = scan_number
    if should_store_location:
        poster.first_scan_latitude = latitude
        poster.first_scan_longitude = longitude
        poster.first_scan_accuracy_m = accuracy
        poster.first_scan_at = timezone.now()
    poster.save()

    return should_store_location


@api_view(["POST"])
@admin_required
def create_poster_campaign(request):
    label = (request.data.get("label") or "").strip()
    if not label:
        return Response(
            {"error": "label is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    destination_url = (request.data.get("destination_url") or "").strip() or None
    base_url = (request.data.get("base_url") or "").strip() or None
    poster = PosterCampaign.objects.create(
        label=label,
        destination_url=destination_url,
        created_by=getattr(request, "user_id", None),
    )
    return Response(_poster_payload(poster, base_url), status=status.HTTP_201_CREATED)


@api_view(["GET"])
@admin_required
def list_poster_campaigns(request):
    base_url = (request.query_params.get("base_url") or "").strip() or None
    posters = PosterCampaign.objects.all()[:50]
    return Response(
        {"posters": [_poster_payload(poster, base_url) for poster in posters]}
    )


@api_view(["GET"])
@admin_required
def list_poster_scans(request):
    poster_id = (request.query_params.get("poster_id") or "").strip()
    scans = PosterScan.objects.select_related("poster")
    if poster_id:
        scans = scans.filter(poster_id=poster_id)
    return Response({"scans": [_scan_payload(scan) for scan in scans[:500]]})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_poster_scan_status(request, poster_id):
    try:
        poster = PosterCampaign.objects.get(id=poster_id)
    except PosterCampaign.DoesNotExist:
        return Response({"error": "Poster not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response(
        {
            "id": str(poster.id),
            "destination_url": poster.destination_url,
            "scan_count": poster.scan_count,
            "needs_location": not poster.has_first_location,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def record_poster_scan(request, poster_id):
    try:
        latitude = _parse_coordinate(request.data.get("latitude"), -90, 90)
        longitude = _parse_coordinate(request.data.get("longitude"), -180, 180)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        accuracy = _parse_accuracy(request.data.get("accuracy_m"))
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        try:
            poster = PosterCampaign.objects.select_for_update().get(id=poster_id)
        except PosterCampaign.DoesNotExist:
            return Response(
                {"error": "Poster not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        should_store_location = _record_scan_for_poster(
            poster,
            request,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
        )

    return Response(
        {
            "id": str(poster.id),
            "scan_count": poster.scan_count,
            "location_saved": should_store_location,
            "destination_url": poster.destination_url,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def redirect_poster_scan(request, poster_id):
    with transaction.atomic():
        try:
            poster = PosterCampaign.objects.select_for_update().get(id=poster_id)
        except PosterCampaign.DoesNotExist:
            return HttpResponseRedirect(_default_destination_url())

        if not poster.has_first_location:
            return HttpResponseRedirect(_build_scan_url(poster.id))

        _record_scan_for_poster(poster, request)
        destination_url = poster.destination_url or _default_destination_url()

    return HttpResponseRedirect(destination_url)
