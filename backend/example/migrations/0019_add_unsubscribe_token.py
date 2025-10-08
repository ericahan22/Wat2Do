# Generated migration for unsubscribe token field

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example", "0018_newslettersubscriber"),
    ]

    operations = [
        migrations.AddField(
            model_name="newslettersubscriber",
            name="unsubscribe_token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
