from django.contrib import admin

from .models import PosterCampaign, PosterScan


@admin.register(PosterCampaign)
class PosterCampaignAdmin(admin.ModelAdmin):
    list_display = ("label", "id", "scan_count", "first_scan_at", "created_at")
    search_fields = ("label", "id")
    readonly_fields = ("id", "scan_count", "created_at", "updated_at")


@admin.register(PosterScan)
class PosterScanAdmin(admin.ModelAdmin):
    list_display = ("poster", "scan_number", "created_at", "latitude", "longitude")
    search_fields = ("poster__label", "poster__id", "ip_address")
    readonly_fields = ("created_at",)
