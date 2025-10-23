"""
Views for the newsletter app.
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import NewsletterSubscriber


@api_view(["POST"])
@permission_classes([AllowAny])
def newsletter_subscribe(request):
    """Subscribe to the newsletter (no authentication required)"""
    email = request.data.get("email", "").strip().lower()

    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        subscriber = NewsletterSubscriber.get_by_email(email)
        created = False

        if subscriber:
            if subscriber.is_active:
                return Response(
                    {"message": "You're already subscribed to our newsletter!"},
                    status=status.HTTP_200_OK,
                )
            else:
                subscriber.is_active = True
                subscriber.save()
        else:
            subscriber = NewsletterSubscriber.create_subscriber(email)
            created = True

        # Send welcome email with mock events
        from services.email_service import email_service

        email_sent = email_service.send_welcome_email(
            subscriber.get_email(), str(subscriber.unsubscribe_token)
        )

        if email_sent:
            return Response(
                {
                    "message": "Successfully subscribed! Check your email for upcoming events.",
                    "email": subscriber.get_email_display(),
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "Subscribed successfully, but email could not be sent. Please check back later.",
                    "email": subscriber.get_email_display(),
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

    except Exception as e:
        return Response(
            {"error": f"Failed to subscribe: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def newsletter_unsubscribe(request, token):
    """API endpoint for frontend unsubscribe functionality"""
    try:
        subscriber = NewsletterSubscriber.objects.get(unsubscribe_token=token)

        if request.method == "GET":
            # Return subscriber info for frontend
            return Response(
                {
                    "already_unsubscribed": not subscriber.is_active,
                    "email": subscriber.get_email_display(),
                    "message": "Already unsubscribed"
                    if not subscriber.is_active
                    else "Ready to unsubscribe",
                    "unsubscribed_at": subscriber.unsubscribed_at,
                }
            )

        # POST - Process unsubscribe
        if not subscriber.is_active:
            return Response(
                {"error": "Already unsubscribed"}, status=status.HTTP_400_BAD_REQUEST
            )

        reason = request.data.get("reason", "").strip()
        feedback = request.data.get("feedback", "").strip()
        full_reason = f"{reason} - {feedback}" if feedback else reason

        subscriber.is_active = False
        subscriber.unsubscribe_reason = full_reason[:255]
        subscriber.unsubscribed_at = timezone.now()
        subscriber.save()

        return Response(
            {
                "message": "Successfully unsubscribed from the newsletter.",
                "email": subscriber.get_email_display(),
                "unsubscribed_at": subscriber.unsubscribed_at,
            }
        )

    except NewsletterSubscriber.DoesNotExist:
        return Response(
            {"error": "Invalid unsubscribe token"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to process request: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def test_email(request):
    """Internal testing route to send test email to e22han@uwaterloo.ca"""
    try:
        from services.email_service import email_service

        # Send test newsletter email
        email_sent = email_service.send_newsletter_email(
            "e22han@uwaterloo.ca", "test-unsubscribe-token"
        )

        if email_sent:
            return Response(
                {
                    "message": "Test email sent successfully to e22han@uwaterloo.ca",
                    "status": "success",
                }
            )
        else:
            return Response(
                {"message": "Failed to send test email", "status": "error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    except Exception as e:
        return Response(
            {"error": f"Failed to send test email: {e!s}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
