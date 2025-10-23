"""
URL configuration for core app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("auth/signup/", views.signup, name="signup"),
    path("auth/login/", views.login_email, name="login"),
    path("auth/me/", views.user_info, name="me"),
    path("auth/logout/", views.logout_user, name="logout"),
    path("auth/confirm/<str:token>/", views.confirm_email, name="confirm_email"),
    path(
        "auth/resend-confirmation/",
        views.resend_confirmation,
        name="resend_confirmation",
    ),
    path("auth/forgot-password/", views.forgot_password, name="forgot_password"),
    path(
        "auth/reset-password/<str:token>/", views.reset_password, name="reset_password"
    ),
    path("auth/csrf-token/", views.get_csrf_token, name="get_csrf_token"),
    path("protected/", views.protected_view, name="protected"),
]
