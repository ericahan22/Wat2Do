"""
URL configuration for events app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_events, name="events"),
    path("<int:event_id>/", views.get_event, name="event_detail"),
    path("export.ics", views.export_events_ics, name="export_events_ics"),
    path(
        "google-calendar-urls/",
        views.get_google_calendar_urls,
        name="get_google_calendar_urls",
    ),
    # Event submission endpoints
    path("submit/", views.submit_event, name="submit_event"),
    path("my-submissions/", views.get_user_submissions, name="get_user_submissions"),
    path("submissions/", views.get_submissions, name="get_submissions"),
    path("submissions/<int:submission_id>/process/", views.process_submission, name="process_submission"),
    path("submissions/<int:submission_id>/review/", views.review_submission, name="review_submission"),
    # Test endpoints
    path("test-similarity/", views.test_similarity, name="test_similarity"),
]
