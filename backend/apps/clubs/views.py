"""
Views for the clubs app.
"""

import json

from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Clubs


@api_view(["GET"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="60/hr", block=True)
def get_clubs(request):
    """Get clubs with cursor-based pagination for infinite scroll"""
    try:
        search_term = request.GET.get("search", "").strip()
        category_filter = request.GET.get("category", "").strip()
        cursor = request.GET.get("cursor", "").strip()
        limit = 50

        queryset = Clubs.objects.all().order_by("id")

        # Apply search filter
        if search_term:
            queryset = queryset.filter(club_name__icontains=search_term)

        # Apply category filter
        if category_filter and category_filter.lower() != "all":
            queryset = queryset.filter(categories__icontains=category_filter)

        # Handle cursor-based pagination
        if cursor:
            try:
                cursor_id = int(cursor)
                queryset = queryset.filter(id__gt=cursor_id)
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid cursor format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get total count for the filtered queryset
        total_count = queryset.count()

        # Fetch one more than limit to check if there are more results
        results = list(
            queryset.values(
                "id",
                "club_name",
                "categories",
                "club_page",
                "ig",
                "discord",
                "club_type",
            )[: limit + 1]
        )

        # Determine if there's a next page
        has_more = len(results) > limit
        if has_more:
            results = results[:limit]  # Remove the extra item

            # Generate next cursor from last item
            last_club = results[-1]
            next_cursor = str(last_club["id"])
        else:
            next_cursor = None

        # Ensure categories is always a list for each club
        for club in results:
            categories = club.get("categories")
            if categories:
                if isinstance(categories, str):
                    try:
                        club["categories"] = json.loads(categories)
                    except json.JSONDecodeError:
                        club["categories"] = [categories] if categories else []
                elif not isinstance(categories, list):
                    club["categories"] = [categories] if categories else []
            else:
                club["categories"] = []

        return Response(
            {
                "results": results,
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "totalCount": total_count,
            }
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
