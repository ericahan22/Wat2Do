"""
URL configuration for events app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_events, name="events"),
    path("export.ics", views.export_events_ics, name="export_events_ics"),
    path(
        "google-calendar-urls/",
        views.get_google_calendar_urls,
        name="get_google_calendar_urls",
    ),
    # Test endpoints
    path("test-similarity/", views.test_similarity, name="test_similarity"),
]
