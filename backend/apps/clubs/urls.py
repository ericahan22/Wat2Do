"""
URL configuration for clubs app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_clubs, name="clubs"),
    
    # Club submission endpoints
    path("submit/", views.submit_club, name="submit_club"),
    path("submissions/", views.get_user_club_submissions, name="get_user_club_submissions"),
    path("submissions/pending/", views.get_pending_club_submissions, name="get_pending_club_submissions"),
    path("submissions/<int:club_id>/moderate/", views.moderate_club, name="moderate_club"),
]
