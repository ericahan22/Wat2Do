import os
import sys
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import django

django.setup()

from django.utils import timezone

from apps.events.models import IgnoredPost


def purge_old_ignored_posts(days=30):
    cutoff = timezone.now() - timedelta(days=days)
    old_posts = IgnoredPost.objects.filter(added_at__lt=cutoff)
    count = old_posts.count()
    old_posts.delete()
    print(f"Purged {count} IgnoredPost rows older than {days} days.")


if __name__ == "__main__":
    purge_old_ignored_posts()
