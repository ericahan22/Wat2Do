from django.db import models

class Clubs(models.Model):
    club_name = models.CharField(max_length=100, unique=True)
    categories = models.CharField(max_length=255)
    club_page = models.URLField(blank=True, null=True)
    ig = models.URLField(blank=True, null=True)  # Changed from insta_url to ig
    discord = models.URLField(blank=True, null=True)  # Added discord field
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

    class Meta:
        db_table = 'clubs'  # Remove api_ prefix

    def __str__(self):
        return self.club_name

class Events(models.Model):
    club_handle = models.CharField(max_length=100, blank=True, null=True)  # Made nullable
    url = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)
    price = models.FloatField(blank=True, null=True)
    food = models.CharField(max_length=255, blank=True, null=True)
    registration = models.BooleanField(default=False)

    class Meta:
        db_table = 'events'  # Remove api_ prefix

    def __str__(self):
        return self.name
