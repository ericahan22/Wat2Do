"""
URL configuration for newsletter app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path(
        "unsubscribe/<uuid:token>/",
        views.newsletter_unsubscribe,
        name="newsletter_unsubscribe",
    ),
    path("test-email/", views.test_email, name="test_email"),
]
