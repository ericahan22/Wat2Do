"""
URL configuration for events app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_events, name="events"),
    path("<int:event_id>/", views.get_event, name="event_detail"),
    path("<int:event_id>/update/", views.update_event, name="update_event"),
    path("<int:event_id>/delete/", views.delete_event, name="delete_event"),
    path("export.ics", views.export_events_ics, name="export_events_ics"),
    path(
        "google-calendar-urls/",
        views.get_google_calendar_urls,
        name="get_google_calendar_urls",
    ),
    # Event submission endpoints
    path("extract/", views.extract_event_from_screenshot, name="extract_event_from_screenshot"),
    path("submit/", views.submit_event, name="submit_event"),
    path("my-submissions/", views.get_user_submissions, name="get_user_submissions"),
    path("submissions/", views.get_submissions, name="get_submissions"),
    path("submissions/<int:event_id>/review/", views.review_submission, name="review_submission"),
    path("submissions/<int:event_id>/", views.delete_submission, name="delete_submission"),
    # Event interest endpoints
    path("my-interests/", views.get_my_interested_event_ids, name="get_my_interested_event_ids"),
    path("<int:event_id>/interest/mark/", views.mark_event_interest, name="mark_event_interest"),
    path("<int:event_id>/interest/unmark/", views.unmark_event_interest, name="unmark_event_interest"),
]
