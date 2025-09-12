"""
Views for the app.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Clubs, Events 
from django.core.serializers import serialize
import json
from django.db.models import Subquery, OuterRef 
from datetime import datetime
from pytz import timezone 


@api_view(["GET"])
def home(request):
    """Home endpoint with basic info"""
    return Response(
        {
            "message": "Instagram Event Scraper API",
            "endpoints": {
                "GET /api/events/?view=grid": "Get events in grid view",
                "GET /api/events/?view=calendar": "Get events in calendar view",
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
    """Get all events from database (no pagination). Event categories are based on club categories"""
    try:
        search_term = request.GET.get('search', '').strip()  # Get search term 
        category_filter = request.GET.get('category', '').strip() 
        view = request.GET.get('view', 'grid')
        
        # Build base queryset
        base_queryset = Events.objects.all().order_by('date', 'start_time')
        
        # Apply filters to create filtered queryset
        filtered_queryset = base_queryset
        
        # Hide past events in grid view only
        if view == 'grid':
            # Include events from today onwards (interpret as EST)
            est = timezone('America/New_York')
            today = datetime.now(est).date()
            filtered_queryset = filtered_queryset.filter(date__gte=today)
        
        if search_term:
            filtered_queryset = filtered_queryset.filter(name__icontains=search_term)
        if category_filter and category_filter.lower() != 'all':
            filtered_queryset = filtered_queryset.filter(
                club_handle__in=Clubs.objects.filter(
                    categories__icontains=category_filter
                ).values('ig')
            )
            
        filtered_queryset = filtered_queryset.annotate(
            club_categories=Subquery(
                Clubs.objects.filter(ig=OuterRef('club_handle')).values('categories')[:1]
            ),
            club_type=Subquery(
                Clubs.objects.filter(ig=OuterRef('club_handle')).values('club_type')[:1]
            )
        )
        
        # Convert to list of dictionaries (no pagination)
        events_data = [
            {
                'id': event.id,
                'club_handle': event.club_handle,
                'url': event.url,
                'name': event.name,
                'date': event.date.isoformat() if event.date else None,
                'start_time': event.start_time.isoformat() if event.start_time else None,
                'end_time': event.end_time.isoformat() if event.end_time else None,
                'location': event.location,
                'category': event.club_categories,
                'club_type': event.club_type,
                'price': event.price,
                'food': event.food,
                'drinks': event.drinks,
                'snacks': event.snacks,
                'registration': event.registration,
            }
            for event in filtered_queryset
        ]
        
        return Response({
            "events": events_data,
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_clubs(request):
    """Get all clubs from database (no pagination)"""
    try:
        search_term = request.GET.get('search', '').strip()  # Get search term
        category_filter = request.GET.get('category', '').strip()  # Get category filter
        
        # Build base queryset
        base_queryset = Clubs.objects.all()
        
        # Apply filters to create filtered queryset
        filtered_queryset = base_queryset
        if search_term:
            filtered_queryset = filtered_queryset.filter(club_name__icontains=search_term)
        if category_filter and category_filter.lower() != 'all':
            filtered_queryset = filtered_queryset.filter(categories__icontains=category_filter)
        
        # Convert to list of dictionaries
        clubs_data = [
            {
                'id': club.id,
                'club_name': club.club_name,
                'categories': club.categories,
                'club_page': club.club_page,
                'ig': club.ig,
                'discord': club.discord,
            }
            for club in filtered_queryset
        ]
        
        return Response({
            "clubs": clubs_data
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
