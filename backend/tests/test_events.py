from django.test import TestCase
from apps.events.models import Events


class EventsModelTest(TestCase):
    def test_event_creation(self):
        """Test creating an event."""
        event = Events.objects.create(
            name="Test Event",
            date="2025-10-15",
            start_time="10:00:00",
            end_time="12:00:00",
            location="Test Location"
        )
        self.assertEqual(event.name, "Test Event")
        self.assertEqual(str(event), "Test Event")
