"""
URL configuration for app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("events/", views.get_events, name="events"),
    path("events/export.ics", views.export_events_ics, name="export_events_ics"),
    path("events/google-calendar-urls/", views.get_google_calendar_urls, name="get_google_calendar_urls"),
    path("clubs/", views.get_clubs, name="clubs"),
    # test endpoints
    path("mock-event/", views.create_mock_event, name="create_mock_event"),
    path("test-similarity/", views.test_similarity, name="test_similarity"),
    # auth endpoints
    path("auth/token/", views.create_auth_token, name="create_auth_token"),
    path("auth/register/", views.create_user, name="create_user"),
    # newsletter endpoints
    path(
        "newsletter/subscribe", views.newsletter_subscribe, name="newsletter_subscribe"
    ),
    path(
        "newsletter/unsubscribe/<uuid:token>",
        views.newsletter_unsubscribe,
        name="newsletter_unsubscribe",
    ),
]
