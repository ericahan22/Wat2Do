# Generated manually for encrypted email support

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("newsletter", "0002_auto_20251013_0521"),
    ]

    operations = [
        # Add the encrypted email field as nullable first
        migrations.AddField(
            model_name="newslettersubscriber",
            name="email_encrypted",
            field=models.TextField(
                blank=True, null=True, help_text="Encrypted email address"
            ),
        ),
        # Since we have no existing data, we can make it non-nullable
        migrations.AlterField(
            model_name="newslettersubscriber",
            name="email_encrypted",
            field=models.TextField(help_text="Encrypted email address"),
        ),
    ]
