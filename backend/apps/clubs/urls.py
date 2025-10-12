"""
URL configuration for clubs app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_clubs, name="clubs"),
]
