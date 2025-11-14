# Generated manually for query optimization

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0024_eventinterest"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="events",
            index=models.Index(
                fields=["school", "status", "dtstart_utc", "dtend_utc"],
                name="events_query_opt_idx",
            ),
        ),
    ]
