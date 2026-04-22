import hmac
from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.clubs.models import Clubs
from apps.core.auth import admin_required
from apps.events.models import Events

from .models import AutomateLog, ScrapeRun


def webhook_key_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        expected = getattr(settings, "AUTOMATE_WEBHOOK_KEY", None)
        if not expected:
            return Response(
                {"error": "Webhook not configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return Response({"error": "Missing API key"}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header[7:]
        if not hmac.compare_digest(token, expected):
            return Response({"error": "Invalid API key"}, status=status.HTTP_403_FORBIDDEN)
        return view_func(request, *args, **kwargs)

    return _wrapped


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@webhook_key_required
def automate_log(request):
    data = request.data
    if not data.get("ig_user_id") and not data.get("ig_username"):
        return Response(
            {"error": "ig_user_id or ig_username required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    AutomateLog.objects.create(
        ig_user_id=data.get("ig_user_id"),
        ig_username=data.get("ig_username"),
        username_resolved=data.get("username_resolved", False),
        dispatch_sent=data.get("dispatch_sent", False),
        error_message=data.get("error_message"),
    )
    return Response({"status": "logged"}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@admin_required
def get_automate_logs(request):
    days = int(request.GET.get("days", 7))
    limit = min(int(request.GET.get("limit", 50)), 200)
    username = request.GET.get("username")

    since = timezone.now() - timedelta(days=days)
    qs = AutomateLog.objects.filter(created_at__gte=since)
    if username:
        qs = qs.filter(ig_username__icontains=username)

    total = qs.count()
    unresolved_count = qs.filter(username_resolved=False).count()
    logs = list(
        qs[:limit].values(
            "id",
            "ig_user_id",
            "ig_username",
            "username_resolved",
            "dispatch_sent",
            "error_message",
            "created_at",
        )
    )
    return Response({"logs": logs, "total": total, "unresolved_count": unresolved_count})


@api_view(["GET"])
@admin_required
def get_scrape_runs(request):
    days = int(request.GET.get("days", 7))
    limit = min(int(request.GET.get("limit", 50)), 200)
    username = request.GET.get("username")
    status_filter = request.GET.get("status")

    since = timezone.now() - timedelta(days=days)
    qs = ScrapeRun.objects.filter(started_at__gte=since)
    if username:
        qs = qs.filter(ig_username__icontains=username)
    if status_filter:
        qs = qs.filter(status=status_filter)

    total = qs.count()
    runs = list(
        qs[:limit].values(
            "id",
            "ig_username",
            "github_run_id",
            "status",
            "posts_fetched",
            "posts_new",
            "events_extracted",
            "events_saved",
            "pinned_post_warning",
            "error_message",
            "started_at",
            "finished_at",
        )
    )
    return Response({"runs": runs, "total": total})


def _extract_ig_username(ig_url):
    if not ig_url:
        return None
    return ig_url.rstrip("/").split("/")[-1]


@api_view(["GET"])
@admin_required
def get_gap_analysis(request):
    clubs = Clubs.objects.all()
    now = timezone.now()

    accounts = []
    for club in clubs:
        ig_handle = _extract_ig_username(club.ig)
        if not ig_handle:
            continue

        last_scrape = (
            ScrapeRun.objects.filter(ig_username=ig_handle)
            .order_by("-started_at")
            .values("started_at", "status")
            .first()
        )

        last_event = (
            Events.objects.filter(ig_handle=ig_handle)
            .order_by("-added_at")
            .values("added_at", "title")
            .first()
        )

        last_notification = (
            AutomateLog.objects.filter(ig_username=ig_handle)
            .order_by("-created_at")
            .values("created_at")
            .first()
        )

        last_event_at = last_event["added_at"] if last_event else None
        gap_days = (now - last_event_at).days if last_event_at else None

        if last_event_at and (now - last_event_at).days <= 7:
            account_status = "active"
        elif last_event_at:
            account_status = "stale"
        else:
            account_status = "never_scraped"

        if last_scrape and last_scrape["status"] == "error":
            account_status = "error"

        accounts.append(
            {
                "ig_handle": ig_handle,
                "club_name": club.club_name,
                "last_notification_at": last_notification["created_at"] if last_notification else None,
                "last_scrape_at": last_scrape["started_at"] if last_scrape else None,
                "last_scrape_status": last_scrape["status"] if last_scrape else None,
                "last_event_at": last_event_at,
                "last_event_title": last_event["title"] if last_event else None,
                "gap_days": gap_days,
                "status": account_status,
            }
        )

    accounts.sort(key=lambda a: (a["gap_days"] is None, -(a["gap_days"] or 0)))

    summary = {
        "total_clubs": len(accounts),
        "active_recently": sum(1 for a in accounts if a["status"] == "active"),
        "stale": sum(1 for a in accounts if a["status"] == "stale"),
        "never_scraped": sum(1 for a in accounts if a["status"] == "never_scraped"),
    }

    return Response({"accounts": accounts, "summary": summary})
