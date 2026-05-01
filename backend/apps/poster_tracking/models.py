import uuid

from django.db import models


class PosterCampaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255)
    destination_url = models.URLField(
        blank=True,
        null=True,
        help_text="Where scanners should be redirected after the scan is recorded.",
    )
    scan_count = models.PositiveIntegerField(default=0)
    first_scan_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    first_scan_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    first_scan_accuracy_m = models.FloatField(null=True, blank=True)
    first_scan_at = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "poster_campaigns"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"], name="poster_campaign_created_idx"),
        ]

    @property
    def has_first_location(self):
        return (
            self.first_scan_latitude is not None
            and self.first_scan_longitude is not None
        )

    def __str__(self):
        return f"{self.label} ({self.id})"


class PosterScan(models.Model):
    poster = models.ForeignKey(
        PosterCampaign,
        on_delete=models.CASCADE,
        related_name="scans",
    )
    scan_number = models.PositiveIntegerField()
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    accuracy_m = models.FloatField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    referrer = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "poster_scans"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["poster", "scan_number"],
                name="unique_scan_number_per_poster",
            ),
        ]
        indexes = [
            models.Index(
                fields=["poster", "created_at"], name="poster_scan_created_idx"
            ),
        ]

    def __str__(self):
        return f"Scan {self.scan_number} for {self.poster_id}"
