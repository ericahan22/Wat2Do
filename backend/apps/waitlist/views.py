from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import SCHOOL_CONFIG, WaitlistEntry


@api_view(["GET"])
@permission_classes([AllowAny])
def get_school_info(request, school_slug):
    """Get information about a school for the waitlist page"""
    if not WaitlistEntry.is_valid_school(school_slug):
        return Response(
            {"error": "School not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    config = SCHOOL_CONFIG[school_slug]
    return Response(
        {
            "slug": school_slug,
            "name": config["name"],
            "domains": config["domains"],
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def list_schools(request):
    """List all available schools for waitlist"""
    schools = [
        {
            "slug": slug,
            "name": config["name"],
            "domains": config["domains"],
        }
        for slug, config in SCHOOL_CONFIG.items()
    ]
    return Response({"schools": schools})


@api_view(["POST"])
@permission_classes([AllowAny])
def join_waitlist(request, school_slug):
    """Join the waitlist for a specific school"""
    email = request.data.get("email", "").strip().lower()

    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate school
    if not WaitlistEntry.is_valid_school(school_slug):
        return Response(
            {"error": "School not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Validate email domain for this school
    is_valid, error_msg = WaitlistEntry.validate_email_for_school(email, school_slug)
    if not is_valid:
        return Response(
            {"error": error_msg},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        entry = WaitlistEntry.create_entry(email, school_slug)
        return Response(
            {
                "message": "You've been added to the waitlist!",
                "email": entry.get_email_display(),
                "school": entry.school_name,
            },
            status=status.HTTP_201_CREATED,
        )
    except IntegrityError:
        return Response(
            {"message": "You're already on the waitlist for this school!"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to join waitlist: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
