"""
Views for the app.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Clubs, Events
from django.core.serializers import serialize
import json


@api_view(["GET"])
def home(request):
    """Home endpoint with basic info"""
    return Response(
        {
            "message": "Instagram Event Scraper API",
            "endpoints": {
                "GET /api/events/": "Get all events from database",
                "GET /api/clubs/": "Get all clubs from database",
                "GET /api/health/": "Health check",
            },
        }
    )


@api_view(["GET"])
def health(request):
    """Health check endpoint"""
    return Response({"status": "healthy", "message": "Server is running"})


@api_view(["GET"])
def get_events(request):
    """Get events from database with pagination and search support"""
    try:
        # Get pagination parameters
        limit = int(request.GET.get('limit', 20))  # Default 20 events per page
        offset = int(request.GET.get('offset', 0))  # Default offset 0
        search_term = request.GET.get('search', '').strip()  # Get search term
        
        # Limit the maximum number of events per request
        limit = min(limit, 100)  # Max 100 events per request
        
        # Build base queryset
        base_queryset = Events.objects.all()
        
        # TOTAL COUNT: Get count of ALL items in database (no filters)
        total_count = base_queryset.count()
        
        # Apply filters to create filtered queryset
        filtered_queryset = base_queryset
        if search_term:
            filtered_queryset = filtered_queryset.filter(name__icontains=search_term)
        
        # QUERY COUNT: Get total count of items matching the filters (no pagination)
        total_query_count = filtered_queryset.count()
        
        # SEPARATE DATA QUERY: Get paginated events from the filtered queryset
        paginated_events = filtered_queryset[offset:offset + limit]
        
        # Convert to list of dictionaries
        events_data = []
        for event in paginated_events:
            events_data.append({
                'id': event.id,
                'club_handle': event.club_handle,
                'url': event.url,
                'name': event.name,
                'date': event.date.isoformat() if event.date else None,
                'start_time': event.start_time.isoformat() if event.start_time else None,
                'end_time': event.end_time.isoformat() if event.end_time else None,
                'location': event.location,
            })
        
        # Check if there are more events to load
        has_more = offset + limit < total_query_count
        next_offset = offset + limit if has_more else None
        
        return Response({
            "count": len(events_data),  # Number of events in this page response
            "total_count": total_count,  # Total count of ALL events in database
            "total_query_count": total_query_count,  # Total count of events matching filters
            "events": events_data,
            "has_more": has_more,
            "next_offset": next_offset,
            "current_offset": offset,
            "limit": limit
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_clubs(request):
    """Get clubs from database with pagination and search support"""
    try:
        # Get pagination parameters
        limit = int(request.GET.get('limit', 20))  # Default 20 clubs per page
        offset = int(request.GET.get('offset', 0))  # Default offset 0
        search_term = request.GET.get('search', '').strip()  # Get search term
        category_filter = request.GET.get('category', '').strip()  # Get category filter
        
        # Limit the maximum number of clubs per request
        limit = min(limit, 100)  # Max 100 clubs per request
        
        # Build base queryset
        base_queryset = Clubs.objects.all()
        
        # TOTAL COUNT: Get count of ALL items in database (no filters)
        total_count = base_queryset.count()
        
        # Apply filters to create filtered queryset
        filtered_queryset = base_queryset
        if search_term:
            filtered_queryset = filtered_queryset.filter(club_name__icontains=search_term)
        if category_filter and category_filter.lower() != 'all':
            filtered_queryset = filtered_queryset.filter(categories__icontains=category_filter)
        
        # QUERY COUNT: Get total count of items matching the filters (no pagination)
        total_query_count = filtered_queryset.count()
        
        # SEPARATE DATA QUERY: Get paginated clubs from the filtered queryset
        paginated_clubs = filtered_queryset[offset:offset + limit]
        
        # Convert to list of dictionaries
        clubs_data = []
        for club in paginated_clubs:
            clubs_data.append({
                'id': club.id,
                'club_name': club.club_name,
                'categories': club.categories,
                'club_page': club.club_page,
                'ig': club.ig,
                'discord': club.discord,
            })
        
        # Check if there are more clubs to load
        has_more = offset + limit < total_query_count
        next_offset = offset + limit if has_more else None
        
        return Response({
            "count": len(clubs_data),  # Number of clubs in this page response
            "total_count": total_count,  # Total count of ALL clubs in database
            "total_query_count": total_query_count,  # Total count of clubs matching filters
            "clubs": clubs_data,
            "has_more": has_more,
            "next_offset": next_offset,
            "current_offset": offset,
            "limit": limit
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
