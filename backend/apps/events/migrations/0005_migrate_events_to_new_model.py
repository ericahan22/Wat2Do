# Generated migration to transform Events table to new Event model

from django.db import migrations, models
from django.contrib.gis.db import models as gis_models
from django.utils import timezone
from datetime import datetime, time as dt_time
import pytz
from pgvector.django import VectorField


def migrate_events_data(apps, schema_editor):
    """
    Migrate data from old Events model to new Event model structure.
    This handles the field mappings and data transformations.
    """
    # Get the old Events model
    Events = apps.get_model('events', 'Events')
    Event = apps.get_model('events', 'Event')
    
    # Get all existing events
    old_events = Events.objects.all()
    
    for old_event in old_events:
        # Create new Event instance
        new_event = Event()
        
        # Map fields that remain the same
        new_event.description = old_event.description
        new_event.location = old_event.location
        new_event.food = old_event.food
        new_event.price = old_event.price
        new_event.registration = old_event.registration
        new_event.embedding = old_event.embedding
        new_event.added_at = old_event.added_at
        new_event.reactions = old_event.reactions
        new_event.club_type = old_event.club_type
        
        # Map renamed fields
        new_event.title = old_event.name  # name -> title
        new_event.source_url = old_event.url  # url -> source_url
        new_event.source_image_url = old_event.image_url  # image_url -> source_image_url
        new_event.ig_handle = old_event.club_handle  # club_handle -> ig_handle
        
        # Handle datetime conversion
        if old_event.date and old_event.start_time:
            # Combine date and start_time
            start_datetime = datetime.combine(old_event.date, old_event.start_time)
            new_event.dtstart = start_datetime
            
            # Handle end_time
            if old_event.end_time:
                end_datetime = datetime.combine(old_event.date, old_event.end_time)
                new_event.dtend = end_datetime
                
                # Calculate duration
                duration = end_datetime - start_datetime
                new_event.duration = duration
            else:
                new_event.dtend = None
                new_event.duration = None
            
            # For UTC conversion, we'll assume local timezone is UTC for now
            # In production, you might want to use a specific timezone
            new_event.dtstart_utc = start_datetime.replace(tzinfo=pytz.UTC)
            if new_event.dtend:
                new_event.dtend_utc = new_event.dtend.replace(tzinfo=pytz.UTC)
            else:
                new_event.dtend_utc = None
            
            # Set canonical UTC timestamps
            new_event.utc_start_ts = new_event.dtstart_utc
            new_event.utc_end_ts = new_event.dtend_utc
            
            # Set dtstamp to when the event was added
            new_event.dtstamp = old_event.added_at or timezone.now()
        else:
            # Handle cases where date/time might be missing
            new_event.dtstart = timezone.now()
            new_event.dtend = None
            new_event.dtstart_utc = timezone.now()
            new_event.dtend_utc = None
            new_event.utc_start_ts = timezone.now()
            new_event.utc_end_ts = None
            new_event.dtstamp = timezone.now()
            new_event.duration = None
        
        # Set defaults for new fields
        new_event.all_day = False
        new_event.tz = 'UTC'  # Default timezone
        new_event.status = 'CONFIRMED'  # Default status
        
        # Create raw_json from old event data
        new_event.raw_json = {
            'migrated_from': 'old_events_table',
            'original_id': old_event.id,
            'original_name': old_event.name,
            'original_date': old_event.date.isoformat() if old_event.date else None,
            'original_start_time': old_event.start_time.isoformat() if old_event.start_time else None,
            'original_end_time': old_event.end_time.isoformat() if old_event.end_time else None,
            'original_club_handle': old_event.club_handle,
            'original_url': old_event.url,
            'original_image_url': old_event.image_url,
            'original_club_type': old_event.club_type,
        }
        
        # Save the new event
        new_event.save()


def reverse_migrate_events_data(apps, schema_editor):
    """
    Reverse migration - convert new Event data back to old Events structure.
    """
    Event = apps.get_model('events', 'Event')
    Events = apps.get_model('events', 'Events')
    
    # Get all new events
    new_events = Event.objects.all()
    
    for new_event in new_events:
        # Create old Events instance
        old_event = Events()
        
        # Map fields back
        old_event.name = new_event.title
        old_event.url = new_event.source_url
        old_event.image_url = new_event.source_image_url
        old_event.club_handle = new_event.ig_handle
        old_event.description = new_event.description
        old_event.location = new_event.location
        old_event.food = new_event.food
        old_event.price = new_event.price
        old_event.registration = new_event.registration
        old_event.embedding = new_event.embedding
        old_event.added_at = new_event.added_at
        old_event.reactions = new_event.reactions
        old_event.club_type = new_event.club_type
        
        # Convert datetime back to date and time
        if new_event.dtstart:
            old_event.date = new_event.dtstart.date()
            old_event.start_time = new_event.dtstart.time()
        else:
            old_event.date = timezone.now().date()
            old_event.start_time = timezone.now().time()
        
        if new_event.dtend:
            old_event.end_time = new_event.dtend.time()
        else:
            old_event.end_time = None
        
        # Save the old event
        old_event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_alter_events_end_time'),
    ]

    operations = [
        # First, create the new Event model
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, help_text="'Spring Career Fair 2024'", null=True)),
                ('description', models.TextField(blank=True, help_text="'Join us for our annual career fair featuring 50+ companies...'", null=True)),
                ('location', models.TextField(blank=True, help_text="'Student Center Ballroom, 123 University Ave'", null=True)),
                ('dtstamp', models.DateTimeField(help_text="'2024-03-15T10:30:00Z'")),
                ('dtstart', models.DateTimeField(help_text="'2024-03-20T09:00:00'")),
                ('dtend', models.DateTimeField(blank=True, help_text="'2024-03-20T17:00:00'", null=True)),
                ('dtstart_utc', models.DateTimeField(help_text="'2024-03-20T14:00:00Z'")),
                ('dtend_utc', models.DateTimeField(blank=True, help_text="'2024-03-20T22:00:00Z'", null=True)),
                ('all_day', models.BooleanField(default=False, help_text='True')),
                ('duration', models.DurationField(blank=True, help_text="'8:00:00'", null=True)),
                ('categories', models.CharField(blank=True, help_text="'Career, Networking, Professional Development'", max_length=255, null=True)),
                ('tz', models.CharField(blank=True, help_text="'America/New_York'", max_length=64, null=True)),
                ('utc_start_ts', models.DateTimeField(blank=True, help_text="'2024-03-20T14:00:00Z'", null=True)),
                ('utc_end_ts', models.DateTimeField(blank=True, help_text="'2024-03-20T22:00:00Z'", null=True)),
                ('rrule', models.TextField(blank=True, help_text="'FREQ=WEEKLY;BYDAY=MO'", null=True)),
                ('rdate', models.JSONField(blank=True, help_text="['2024-03-25', '2024-04-01']", null=True)),
                ('status', models.CharField(blank=True, help_text="Event status (e.g., 'CONFIRMED', 'TENTATIVE', 'CANCELLED')", max_length=32, null=True)),
                ('geo', gis_models.PointField(blank=True, help_text="'POINT(-74.0059 40.7128)'", null=True, srid=4326)),
                ('raw_json', models.JSONField(help_text="{'title': 'Career Fair', 'location': 'Student Center'}")),
                ('source_url', models.TextField(blank=True, help_text="'https://university.edu/events/career-fair'", null=True)),
                ('source_image_url', models.TextField(blank=True, help_text="'https://example.com/image1.jpg,https://example.com/image2.jpg'", null=True)),
                ('reactions', models.JSONField(blank=True, default=dict, help_text="{'likes': 25, 'bookmarks': 12, 'shares': 8}")),
                ('embedding', VectorField(blank=True, dimensions=1536, help_text="[0.1, -0.2, 0.3, ...]", null=True)),
                ('food', models.CharField(blank=True, help_text="'Free pizza and drinks'", max_length=255, null=True)),
                ('registration', models.BooleanField(default=False, help_text='True')),
                ('added_at', models.DateTimeField(auto_now_add=True, help_text="'2024-03-15T10:30:00Z'", null=True)),
                ('price', models.FloatField(blank=True, help_text='15.99', null=True)),
                ('school', models.CharField(blank=True, help_text="'University of Waterloo'", max_length=255, null=True)),
                ('club_type', models.CharField(blank=True, help_text="'Academic, Sports, Cultural'", max_length=50, null=True)),
                ('ig_handle', models.CharField(blank=True, help_text="'@uwcareercenter'", max_length=100, null=True)),
                ('discord_handle', models.CharField(blank=True, help_text="'careercenter#1234'", max_length=100, null=True)),
                ('x_handle', models.CharField(blank=True, help_text="'@UWCareerCenter'", max_length=100, null=True)),
                ('tiktok_handle', models.CharField(blank=True, help_text="'@uwcareercenter'", max_length=100, null=True)),
                ('fb_handle', models.CharField(blank=True, help_text="'@uwcareercenter'", max_length=100, null=True)),
            ],
            options={
                'indexes': [models.Index(fields=['utc_start_ts'], name='events_event_utc_start_ts_idx')],
            },
        ),
        
        # Migrate the data
        migrations.RunPython(
            migrate_events_data,
            reverse_migrate_events_data,
        ),
        
        # Drop the old Events table
        migrations.DeleteModel(
            name='Events',
        ),
    ]
