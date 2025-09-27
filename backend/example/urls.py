"""
URL configuration for app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("events/", views.get_events, name="events"),
    path("clubs/", views.get_clubs, name="clubs"),
    # test endpoints
    path("mock-event/", views.create_mock_event, name="create_mock_event"),
    path("test-similarity/", views.test_similarity, name="test_similarity"),
    # auth endpoints
    path("auth/token/", views.create_auth_token, name="create_auth_token"),
    path("auth/register/", views.create_user, name="create_user"),
]
