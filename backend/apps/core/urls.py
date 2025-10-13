"""
URL configuration for core app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("auth/token/", views.create_auth_token, name="create_auth_token"),
    path("auth/register/", views.create_user, name="create_user"),
]
