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
    """Get all events from database"""
    try:
        events = Events.objects.all()
        
        # Convert to list of dictionaries
        events_data = []
        for event in events:
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
        
        return Response({
            "count": len(events_data), 
            "events": events_data
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_clubs(request):
    """Get clubs from database with pagination support"""
    try:
        # Get pagination parameters
        limit = int(request.GET.get('limit', 20))  # Default 20 clubs per page
        offset = int(request.GET.get('offset', 0))  # Default offset 0
        
        # Limit the maximum number of clubs per request
        limit = min(limit, 100)  # Max 100 clubs per request
        
        # Get total count
        total_count = Clubs.objects.count()
        
        # Get paginated clubs
        clubs = Clubs.objects.all()[offset:offset + limit]
        
        # Convert to list of dictionaries
        clubs_data = []
        for club in clubs:
            clubs_data.append({
                'id': club.id,
                'club_name': club.club_name,
                'categories': club.categories,
                'club_page': club.club_page,
                'ig': club.ig,
                'discord': club.discord,
            })
        
        # Check if there are more clubs to load
        has_more = offset + limit < total_count
        next_offset = offset + limit if has_more else None
        
        return Response({
            "count": len(clubs_data),
            "total_count": total_count,
            "clubs": clubs_data,
            "has_more": has_more,
            "next_offset": next_offset,
            "current_offset": offset,
            "limit": limit
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
