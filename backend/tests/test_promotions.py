from django.test import TestCase
from django.utils import timezone
from apps.events.models import Events
from apps.promotions.models import EventPromotion


class EventPromotionModelTest(TestCase):
    def setUp(self):
        self.event = Events.objects.create(
            name="Test Event",
            date="2025-10-15",
            start_time="10:00:00",
            end_time="12:00:00",
            location="Test Location"
        )

    def test_promotion_creation(self):
        """Test creating an event promotion."""
        promotion = EventPromotion.objects.create(
            event=self.event,
            promoted_by="admin@example.com",
            priority=5,
            promotion_type="featured"
        )
        self.assertEqual(promotion.event, self.event)
        self.assertEqual(promotion.promoted_by, "admin@example.com")
        self.assertTrue(promotion.is_active)
        self.assertFalse(promotion.is_expired)
