"""
Views for the clubs app.
"""

import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import Clubs


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
        clubs_data = []
        for club in filtered_queryset:
            # Ensure categories is always a list
            categories = club.categories if isinstance(club.categories, list) else json.loads(club.categories)
            
            clubs_data.append({
                "id": club.id,
                "club_name": club.club_name,
                "categories": categories,
                "club_page": club.club_page,
                "ig": club.ig,
                "discord": club.discord,
                "club_type": club.club_type,
            })

        return Response({"clubs": clubs_data})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
