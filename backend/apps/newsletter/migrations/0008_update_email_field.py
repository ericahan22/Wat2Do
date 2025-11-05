# Generated migration for newsletter email field update

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0007_revert_to_email_based'),
    ]

    operations = [
        migrations.AddField(
            model_name='newslettersubscriber',
            name='email',
            field=models.EmailField(default='', help_text='Email address'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='newslettersubscriber',
            name='email_encrypted',
        ),
    ]
