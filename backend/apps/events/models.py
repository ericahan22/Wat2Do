from django.db import models
from django.utils import timezone


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

    # Event categorization
    categories = models.JSONField(
        default=list,
        null=True,
        blank=True,
        help_text="['Career', 'Networking']",
    )

    # Event status
    status = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text="Event status (e.g., 'CONFIRMED', 'TENTATIVE', 'CANCELLED')",
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
    other_handle = models.CharField(
        max_length=100, blank=True, null=True, help_text="Other social media handle"
    )

    class Meta:
        db_table = "events"
        indexes = []

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
    submitted_by = models.CharField(
        max_length=255, help_text="Clerk user ID who submitted this event"
    )

    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.CharField(max_length=255, null=True, blank=True)

    created_event = models.ForeignKey(
        Events,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="submission",
    )

    class Meta:
        db_table = "event_submissions"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Submission {self.id} - {self.status}"


class EventDates(models.Model):
    """
    Stores individual occurrence dates for events.
    """

    id = models.BigAutoField(primary_key=True)
    event = models.ForeignKey(
        Events,
        on_delete=models.CASCADE,
        related_name="event_dates",
        db_index=True,
        help_text="Reference to the parent event",
    )
    dtstart_utc = models.DateTimeField(
        db_index=True, help_text="UTC start time for this occurrence"
    )
    dtend_utc = models.DateTimeField(
        blank=True, null=True, help_text="UTC end time for this occurrence"
    )
    duration = models.DurationField(
        blank=True, null=True, help_text="Duration of this occurrence"
    )
    tz = models.CharField(
        max_length=64, null=True, blank=True, help_text="'America/New_York'"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "event_dates"
        indexes = [
            models.Index(fields=["dtstart_utc"], name="eventdates_dtstart_utc_idx"),
            models.Index(fields=["dtend_utc"], name="eventdates_dtend_utc_idx"),
            models.Index(fields=["event", "dtstart_utc"], name="eventdates_event_dtstart_idx"),
        ]
        ordering = ["dtstart_utc"]

    def __str__(self):
        return f"{self.event.title[:30] if self.event.title else 'untitled'} @ {self.dtstart_utc}"


class EventInterest(models.Model):
    """
    Tracks user interest in events.
    Many-to-many relationship between users (Clerk user IDs) and events.
    """
    id = models.BigAutoField(primary_key=True)
    event = models.ForeignKey(
        Events,
        on_delete=models.CASCADE,
        related_name="interests",
        db_index=True,
        help_text="Reference to the event"
    )
    user_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Clerk user ID of the interested user"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "event_interests"
        unique_together = [["event", "user_id"]]
        ordering = ["-created_at"]

    def __str__(self):
        return f"User {self.user_id} interested in {self.event.title[:30] if self.event.title else 'untitled'}"


class IgnoredPost(models.Model):
    shortcode = models.CharField(max_length=32, unique=True)
    added_at = models.DateTimeField(auto_now_add=True)
