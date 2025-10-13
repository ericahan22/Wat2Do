import uuid

from django.db import models


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    unsubscribe_token = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False
    )
    unsubscribe_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Reason provided when user unsubscribed",
    )
    unsubscribed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "newsletter_subscribers"
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email
