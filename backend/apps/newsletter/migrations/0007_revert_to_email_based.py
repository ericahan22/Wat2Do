# Generated manually to revert newsletter to email-based system

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("newsletter", "0006_update_newsletter_model"),
    ]

    operations = [
        # Remove user field
        migrations.RemoveField(
            model_name="newslettersubscriber",
            name="user",
        ),
        # Add back email_encrypted field
        migrations.AddField(
            model_name="newslettersubscriber",
            name="email_encrypted",
            field=models.TextField(help_text="Encrypted email address"),
        ),
    ]
