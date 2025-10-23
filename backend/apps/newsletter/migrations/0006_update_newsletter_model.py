# Generated manually for newsletter model update


import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("newsletter", "0004_alter_newslettersubscriber_email_hash"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        # Remove old fields
        migrations.RemoveField(
            model_name="newslettersubscriber",
            name="email_encrypted",
        ),
        migrations.RemoveField(
            model_name="newslettersubscriber",
            name="email_hash",
        ),
        # Add new user field
        migrations.AddField(
            model_name="newslettersubscriber",
            name="user",
            field=models.ForeignKey(
                help_text="User who subscribed to newsletter",
                on_delete=django.db.models.deletion.CASCADE,
                to="auth.user",
                null=True,  # Allow null initially
                blank=True,
            ),
        ),
        # Make user field non-nullable after data migration
        migrations.AlterField(
            model_name="newslettersubscriber",
            name="user",
            field=models.ForeignKey(
                help_text="User who subscribed to newsletter",
                on_delete=django.db.models.deletion.CASCADE,
                to="auth.user",
            ),
        ),
    ]
