from django.db import models


class AutomateLog(models.Model):
    ig_user_id = models.CharField(max_length=100, blank=True, null=True)
    ig_username = models.CharField(max_length=100, blank=True, null=True)
    username_resolved = models.BooleanField(default=False)
    dispatch_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "automate_logs"
        ordering = ["-created_at"]

    def __str__(self):
        username = self.ig_username or self.ig_user_id or "unknown"
        return f"{username} @ {self.created_at}"


class ScrapeRun(models.Model):
    STATUS_CHOICES = [
        ("running", "Running"),
        ("success", "Success"),
        ("error", "Error"),
        ("no_posts", "No Posts"),
    ]

    ig_username = models.CharField(max_length=100, db_index=True)
    github_run_id = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="running")
    posts_fetched = models.IntegerField(default=0)
    posts_new = models.IntegerField(default=0)
    events_extracted = models.IntegerField(default=0)
    events_saved = models.IntegerField(default=0)
    pinned_post_warning = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "scrape_runs"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.ig_username} — {self.status} @ {self.started_at}"
