from django.db import models


class Clubs(models.Model):
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

    class Meta:
        db_table = "clubs"

    def __str__(self):
        return self.club_name