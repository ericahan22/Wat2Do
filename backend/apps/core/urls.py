"""
URL configuration for core app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("auth/signup/", views.signup_view, name="signup"),
    path("auth/login/", views.login_email_view, name="login"),
    path("auth/me/", views.me_view, name="me"),
    path("auth/logout/", views.logout_view, name="logout"),
]
