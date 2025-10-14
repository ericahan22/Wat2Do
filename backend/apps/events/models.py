from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField


class Events(models.Model):
    STATUS_CHOICES = [
        ('scraped', 'Scraped'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    club_handle = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)
    price = models.FloatField(blank=True, null=True)
    food = models.CharField(max_length=255, blank=True, null=True)
    registration = models.BooleanField(default=False)
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    embedding = VectorField(dimensions=1536, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True, null=True)
    club_type = models.CharField(max_length=50, blank=True, null=True)
    reactions = models.JSONField(default=dict, blank=True)
    notes = models.TextField(
        blank=True, null=True, help_text="Internal notes for this event"
    )
    
    # Submission fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scraped')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_events')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "events"
        ordering = ["date", "start_time"]

    def __str__(self):
        return self.name
