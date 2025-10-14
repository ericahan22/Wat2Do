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
    
    # Event submission endpoints
    path("submit/", views.submit_event, name="submit_event"),
    path("submissions/", views.get_user_submissions, name="get_user_submissions"),
    path("submissions/pending/", views.get_pending_submissions, name="get_pending_submissions"),
    path("submissions/<int:event_id>/moderate/", views.moderate_event, name="moderate_event"),
]
