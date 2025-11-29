from django.urls import path

from . import views

urlpatterns = [
    path("schools/", views.list_schools, name="waitlist-schools"),
    path("<str:school_slug>/", views.get_school_info, name="waitlist-school-info"),
    path("<str:school_slug>/join/", views.join_waitlist, name="waitlist-join"),
]
