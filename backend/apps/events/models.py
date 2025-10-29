from django.db import models
from django.utils import timezone
from pgvector.django import VectorField


class Events(models.Model):
    # Human-readable event information
    id = models.BigAutoField(primary_key=True)
    title = models.TextField(
        null=True, blank=True, help_text="'Spring Career Fair 2024'"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="'Join us for our annual career fair featuring 50+ companies...'",
    )
    location = models.TextField(
        null=True, blank=True, help_text="'Student Center Ballroom, 123 University Ave'"
    )

    # iCalendar datetime fields (RFC 5545 standard)
    dtstamp = models.DateTimeField(
        default=timezone.now, help_text="'time created in UTC, 2024-03-15T10:30:00Z'"
    )
    dtstart = models.DateTimeField(
        default=timezone.now, help_text="'2024-03-20T09:00:00'"
    )
    dtend = models.DateTimeField(
        blank=True, null=True, help_text="'2024-03-20T17:00:00'"
    )
    dtstart_utc = models.DateTimeField(
        default=timezone.now, help_text="'2024-03-20T14:00:00Z'"
    )
    dtend_utc = models.DateTimeField(
        blank=True, null=True, help_text="'2024-03-20T22:00:00Z'"
    )
    all_day = models.BooleanField(default=False, help_text="True")
    duration = models.DurationField(blank=True, null=True, help_text="'8:00:00'")

    # Event categorization
    categories = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="'Career, Networking, Professional Development'",
    )

    # Timezone information
    tz = models.CharField(
        max_length=64, null=True, blank=True, help_text="'America/New_York'"
    )

    # Recurrence rules (iCalendar RFC 5545)
    rrule = models.TextField(null=True, blank=True, help_text="'FREQ=WEEKLY;BYDAY=MO'")
    rdate = models.JSONField(
        null=True, blank=True, help_text="['2024-03-25', '2024-04-01']"
    )

    # Event status
    status = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text="Event status (e.g., 'CONFIRMED', 'TENTATIVE', 'CANCELLED')",
    )

    # Geographic location (regular numeric fields)
    latitude = models.FloatField(null=True, blank=True, help_text="40.7128")
    longitude = models.FloatField(null=True, blank=True, help_text="-74.0059")

    # Data provenance and raw extraction
    raw_json = models.JSONField(
        default=dict, help_text="{'title': 'Career Fair', 'location': 'Student Center'}"
    )
    source_url = models.TextField(
        null=True, blank=True, help_text="'https://university.edu/events/career-fair'"
    )
    source_image_url = models.TextField(
        null=True,
        blank=True,
        help_text="'https://example.com/image1.jpg,https://example.com/image2.jpg'",
    )

    # Additional event metadata
    reactions = models.JSONField(
        default=dict,
        blank=True,
        help_text="{'likes': 25, 'bookmarks': 12, 'shares': 8}",
    )
    embedding = VectorField(
        dimensions=1536, blank=True, null=True, help_text="[0.1, -0.2, 0.3, ...]"
    )
    food = models.CharField(
        max_length=255, blank=True, null=True, help_text="'Free pizza and drinks'"
    )
    registration = models.BooleanField(default=False, help_text="True")
    added_at = models.DateTimeField(
        auto_now_add=True, null=True, help_text="'2024-03-15T10:30:00Z'"
    )
    price = models.FloatField(blank=True, null=True, help_text="15.99")
    school = models.CharField(
        max_length=255, blank=True, null=True, help_text="'University of Waterloo'"
    )
    club_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="WUSA, Athletics, Student Society",
    )

    # Social media handles
    ig_handle = models.CharField(
        max_length=100, blank=True, null=True, help_text="'uwcareercenter'"
    )
    discord_handle = models.CharField(
        max_length=100, blank=True, null=True, help_text="'careercenter#1234'"
    )
    x_handle = models.CharField(
        max_length=100, blank=True, null=True, help_text="'UWCareerCenter'"
    )
    tiktok_handle = models.CharField(
        max_length=100, blank=True, null=True, help_text="'uwcareercenter'"
    )
    fb_handle = models.CharField(
        max_length=100, blank=True, null=True, help_text="'uwcareercenter'"
    )

    class Meta:
        db_table = "events"
        indexes = [
            models.Index(fields=["dtstart_utc"]),
        ]

    def __str__(self):
        return f"{self.title[:50] if self.title else 'untitled'}"


class EventSubmission(models.Model):
    """User-submitted events pending admin review"""

    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    # Submission details
    id = models.BigAutoField(primary_key=True)
    screenshot_url = models.URLField(help_text="S3 URL of uploaded screenshot")
    source_url = models.URLField(help_text="URL to original event source")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    submitted_by = models.CharField(
        max_length=255, null=True, blank=True, help_text="Clerk user ID who submitted this event"
    )

    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.CharField(max_length=255, null=True, blank=True)

    # Extracted event data (populated after OpenAI processing)
    extracted_data = models.JSONField(
        null=True, blank=True, help_text="Event data extracted by OpenAI"
    )

    # Optional: link to created event if approved
    created_event = models.ForeignKey(
        Events, null=True, blank=True, on_delete=models.SET_NULL, related_name="submission"
    )

    # Admin notes
    admin_notes = models.TextField(blank=True)

    class Meta:
        db_table = "event_submissions"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Submission {self.id} - {self.status}"
