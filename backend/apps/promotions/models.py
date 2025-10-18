from django.db import models
from django.utils import timezone


class EventPromotion(models.Model):
    """
    Separate table for event promotions.
    One-to-one relationship with Events table.
    """

    # Primary key is the event (OneToOneField)
    event = models.OneToOneField(
        "events.Events",
        on_delete=models.CASCADE,
        related_name="promotion",
        primary_key=True,
        help_text="Event being promoted",
    )

    # Core promotion fields
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this promotion is currently active",
    )
    promoted_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When this event was promoted"
    )
    promoted_by = models.CharField(
        max_length=100, help_text="Who promoted this event (username or email)"
    )

    # Optional expiration
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When this promotion expires (null = no expiration)",
    )

    # Priority and type
    priority = models.IntegerField(
        default=10,
        db_index=True,
        help_text="Priority level (1-10, higher = more prominent)",
    )
    promotion_type = models.CharField(
        max_length=50,
        default="standard",
        choices=[
            ("standard", "Standard"),
            ("featured", "Featured"),
            ("urgent", "Urgent"),
            ("sponsored", "Sponsored"),
        ],
        help_text="Type of promotion",
    )

    # Internal notes
    notes = models.TextField(
        blank=True, help_text="Internal notes about this promotion"
    )

    class Meta:
        db_table = "event_promotions"
        ordering = ["-priority", "-promoted_at"]

    def __str__(self):
        return f"Promotion for {self.event.title}"

    @property
    def is_expired(self):
        """Check if this promotion has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def is_effective(self):
        """Check if this promotion is currently effective (active and not expired)."""
        return self.is_active and not self.is_expired
