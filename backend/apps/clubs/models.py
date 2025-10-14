from django.db import models
from django.contrib.auth.models import User


class Clubs(models.Model):
    STATUS_CHOICES = [
        ('scraped', 'Scraped'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    club_name = models.CharField(max_length=100, unique=True)
    categories = models.CharField(max_length=255)
    club_page = models.URLField(blank=True, null=True)
    ig = models.URLField(blank=True, null=True)
    discord = models.URLField(blank=True, null=True)
    club_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[
            ("WUSA", "WUSA"),
            ("Athletics", "Athletics"),
            ("Student Society", "Student Society"),
        ],
    )
    
    # Submission fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scraped')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_clubs')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "clubs"

    def __str__(self):
        return self.club_name
