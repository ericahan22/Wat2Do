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
]
