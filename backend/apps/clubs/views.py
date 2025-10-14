"""
Views for the clubs app.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.utils import timezone

from .models import Clubs
from .serializers import ClubSubmissionSerializer, ClubSubmissionResponseSerializer, ClubModerationSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def get_clubs(request):
    """Get all clubs from database (no pagination)"""
    try:
        search_term = request.GET.get("search", "").strip()  # Get search term
        category_filter = request.GET.get("category", "").strip()  # Get category filter

        # Build base queryset - show approved clubs and scraped clubs to public (scraped clubs are auto-approved)
        base_queryset = Clubs.objects.filter(status__in=['approved', 'scraped'])

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
        clubs_data = [
            {
                "id": club.id,
                "club_name": club.club_name,
                "categories": club.categories,
                "club_page": club.club_page,
                "ig": club.ig,
                "discord": club.discord,
                "club_type": club.club_type,
            }
            for club in filtered_queryset
        ]

        return Response({"clubs": clubs_data})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_club(request):
    """Submit a new club for approval"""
    try:
        # Check if user's email is verified
        try:
            profile = request.user.profile
            if not profile.email_verified:
                return Response(
                    {"error": "Email verification required. Please verify your email before submitting clubs."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except:
            return Response(
                {"error": "User profile not found. Please contact support."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = ClubSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            # Create club with submission fields
            club = serializer.save(
                status='pending',
                submitted_by=request.user,
                submitted_at=timezone.now()
            )
            
            response_serializer = ClubSubmissionResponseSerializer(club)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {"error": f"Failed to submit club: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_club_submissions(request):
    """Get user's submitted clubs"""
    try:
        clubs = Clubs.objects.filter(
            submitted_by=request.user,
            status__in=['pending', 'approved', 'rejected']
        ).order_by('-submitted_at')
        
        serializer = ClubSubmissionResponseSerializer(clubs, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {"error": f"Failed to get club submissions: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_pending_club_submissions(request):
    """Admin: Get all pending club submissions"""
    try:
        clubs = Clubs.objects.filter(status='pending').order_by('submitted_at')
        serializer = ClubSubmissionResponseSerializer(clubs, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {"error": f"Failed to get pending club submissions: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def moderate_club(request, club_id):
    """Admin: Approve or reject a club submission"""
    try:
        try:
            club = Clubs.objects.get(id=club_id, status='pending')
        except Clubs.DoesNotExist:
            return Response(
                {"error": "Club not found or not pending"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = ClubModerationSerializer(data=request.data)
        if serializer.is_valid():
            # Update club with moderation decision
            club.status = serializer.validated_data['status']
            club.reviewed_by = request.user
            club.reviewed_at = timezone.now()
            
            if serializer.validated_data['status'] == 'rejected':
                club.rejection_reason = serializer.validated_data['rejection_reason']
            
            club.save()
            
            response_serializer = ClubSubmissionResponseSerializer(club)
            return Response(response_serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {"error": f"Failed to moderate club: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
