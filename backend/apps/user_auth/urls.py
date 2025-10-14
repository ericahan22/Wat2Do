"""
URL configuration for core app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("auth/token/", views.create_auth_token, name="create_auth_token"),
    path("auth/register/", views.create_user, name="create_user"),
    path("auth/verify-email/<str:token>/", views.verify_email, name="verify_email"),
    path("auth/check-verification/", views.check_verification_status, name="check_verification_status"),
    path("auth/resend-verification/", views.resend_verification, name="resend_verification"),
    path("auth/status/", views.check_auth_status, name="check_auth_status"),
    path("auth/logout/", views.logout, name="logout"),
]
