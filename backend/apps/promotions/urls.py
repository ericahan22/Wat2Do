"""
URL configuration for promotions app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("events/promoted/", views.get_promoted_events, name="get_promoted_events"),
    path("events/<int:event_id>/promote/", views.promote_event, name="promote_event"),
    path(
        "events/<int:event_id>/unpromote/",
        views.unpromote_event,
        name="unpromote_event",
    ),
    path(
        "events/<int:event_id>/promotion-status/",
        views.get_promotion_status,
        name="get_promotion_status",
    ),
]
