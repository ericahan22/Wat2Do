from django.urls import path

from . import views

urlpatterns = [
    path("admin/", views.list_poster_campaigns, name="poster-campaigns"),
    path("admin/create/", views.create_poster_campaign, name="poster-campaign-create"),
    path(
        "<uuid:poster_id>/status/", views.get_poster_scan_status, name="poster-status"
    ),
    path("<uuid:poster_id>/scan/", views.record_poster_scan, name="poster-scan"),
    path(
        "<uuid:poster_id>/redirect/",
        views.redirect_poster_scan,
        name="poster-scan-redirect",
    ),
]
