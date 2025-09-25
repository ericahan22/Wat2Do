"""
Views for the app.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Clubs, Events 
import json
from django.db.models import Subquery, OuterRef 
from datetime import datetime, date, time
from pytz import timezone
from .embedding_utils import generate_event_embedding, is_duplicate_event, find_similar_events
from services.openai_service import generate_embedding
from django.db import connection 


@api_view(["GET"])
def home(request):
    """Home endpoint with basic info"""
    return Response(
        {
            "message": "Instagram Event Scraper API with Vector Similarity",
            "endpoints": {
                "GET /api/events/?view=grid": "Get events in grid view",
                "GET /api/events/?view=calendar": "Get events in calendar view",
                "GET /api/clubs/": "Get all clubs from database",
                "GET /api/health/": "Health check",
                "POST /api/mock-event/": "Create a mock event with vector embedding",
                "GET /api/test-similarity/?text=search_text": "Test vector similarity search",
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
            search_embedding = generate_embedding(search_term)
            similar_events = find_similar_events(
                embedding=search_embedding, 
                threshold=0.25
            )
            if similar_events:
                similar_event_ids = [event['id'] for event in similar_events]
                filtered_queryset = filtered_queryset.filter(id__in=similar_event_ids)
            else:
                filtered_queryset = filtered_queryset.none()
        if category_filter and category_filter.lower() != 'all':
            filtered_queryset = filtered_queryset.filter(
                club_handle__in=Clubs.objects.filter(
                    categories__icontains=category_filter
                ).values('ig')
            )
            
        filtered_queryset = filtered_queryset.annotate(
            club_categories=Subquery(
                Clubs.objects.filter(ig=OuterRef('club_handle')).values('categories')[:1]
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
                'registration': event.registration,
                'image_url': event.image_url,
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
                'club_type': club.club_type,
            }
            for club in filtered_queryset
        ]
        
        return Response({
            "clubs": clubs_data
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def create_mock_event(request):
    """Create a mock event with vector embedding for testing"""
    try:
        # Get event data from request or use defaults
        event_data = {
            'name': request.data.get('name', 'Test Event'),
            'location': request.data.get('location', 'Test Location'),
            'food': request.data.get('food', 'Pizza and drinks'),
            'club_handle': request.data.get('club_handle', 'test_club'),
        }
        
        # Check if this would be a duplicate
        embedding = generate_event_embedding(event_data)
        similar_events = find_similar_events(embedding, limit=1)
        
        if similar_events:
            return Response({
                "message": "Duplicate event detected! A similar event already exists.",
                "event_data": event_data,
                "similar_event": similar_events[0]
            }, status=status.HTTP_409_CONFLICT)
        
        # Create the event using raw SQL to handle the vector column
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO events (
                    club_handle, url, name, date, start_time, end_time, 
                    location, price, food, registration, image_url, embedding
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                RETURNING id
            """, [
                event_data['club_handle'],
                request.data.get('url', 'https://example.com'),
                event_data['name'],
                request.data.get('date', date.today()),
                request.data.get('start_time', time(18, 0)),  # 6 PM
                request.data.get('end_time', time(20, 0)),   # 8 PM
                event_data['location'],
                request.data.get('price', 10.0),
                event_data['food'],
                request.data.get('registration', False),
                request.data.get('image_url', 'https://example.com/image.jpg'),
                embedding,
            ])
            
            event_id = cursor.fetchone()[0]
        
        return Response({
            "message": "Mock event created successfully!",
            "event_id": event_id,
            "event_data": event_data,
            "embedding_generated": True
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            "error": f"Failed to create mock event: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def test_similarity(request):
    """Test vector similarity search"""
    try:
        search_text = request.GET.get('text', 'Test Event at Test Location')
        # Generate embedding for search text
        search_embedding = generate_event_embedding(search_text)

        similar_events = find_similar_events(search_embedding, threshold=0.4)
        
        results = []
        if similar_events:
            # Get the actual event details
            event_ids = [event['id'] for event in similar_events]
            events = Events.objects.filter(id__in=event_ids)
            # Create a mapping for quick lookup
            events_dict = {event.id: event for event in events}
            
            for similar_event in similar_events:
                event = events_dict.get(similar_event['id'])
                if event:
                    results.append({
                        'id': event.id,
                        'name': event.name,
                        'similarity': similar_event['similarity']
                    })
        
        return Response({
            "search_text": search_text,
            "similar_events": results
        })
        
    except Exception as e:
        return Response({
            "error": f"Failed to test similarity: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)