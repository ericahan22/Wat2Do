from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("poster_tracking", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="posterscan",
            name="accuracy_m",
        ),
        migrations.RemoveField(
            model_name="posterscan",
            name="latitude",
        ),
        migrations.RemoveField(
            model_name="posterscan",
            name="longitude",
        ),
    ]
