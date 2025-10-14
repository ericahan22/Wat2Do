from django.contrib import admin
from django.urls import include, path

from apps.user_auth import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", views.health, name="health"),
    path("", views.home, name="root"),
    path("api/events/", include("apps.events.urls")),
    path("api/clubs/", include("apps.clubs.urls")),
    path("api/newsletter/", include("apps.newsletter.urls")),
    path("api/promotions/", include("apps.promotions.urls")),
    path("api/", include("apps.user_auth.urls")),
]
