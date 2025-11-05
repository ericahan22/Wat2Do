"""
URL configuration for core app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("auth/me/", views.user_info, name="me"),
    path("protected/", views.protected_view, name="protected"),
]
