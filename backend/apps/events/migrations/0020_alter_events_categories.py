# Migration that exists in production (applied 2025-11-03)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0019_remove_events_events_school_status_dtstart_utc_dtend_utc_added_at_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='categories',
            field=models.JSONField(blank=True, default=list, help_text="['Career', 'Networking']", null=True),
        ),
    ]

