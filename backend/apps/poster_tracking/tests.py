from django.test import TestCase, override_settings

from .models import PosterCampaign, PosterScan


@override_settings(FRONTEND_URL="https://wat2do.ca")
class PosterScanTrackingTests(TestCase):
    def test_record_scan_stores_first_location_on_campaign(self):
        poster = PosterCampaign.objects.create(
            label="Test poster",
            destination_url="https://wat2do.ca/events",
        )

        response = self.client.post(
            f"/api/posters/{poster.id}/scan/",
            {
                "latitude": 43.472285,
                "longitude": -80.544858,
                "accuracy_m": 12.5,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        poster.refresh_from_db()
        self.assertEqual(poster.scan_count, 1)
        self.assertTrue(poster.has_first_location)
        self.assertEqual(str(poster.first_scan_latitude), "43.472285")
        self.assertEqual(str(poster.first_scan_longitude), "-80.544858")
        self.assertEqual(PosterScan.objects.filter(poster=poster).count(), 1)

    def test_redirect_sends_unlocated_poster_to_frontend_without_counting(self):
        poster = PosterCampaign.objects.create(
            label="Test poster",
            destination_url="https://wat2do.ca/events",
        )

        response = self.client.get(f"/api/posters/{poster.id}/redirect/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"https://wat2do.ca/poster/{poster.id}")
        poster.refresh_from_db()
        self.assertEqual(poster.scan_count, 0)
        self.assertFalse(poster.has_first_location)
        self.assertFalse(PosterScan.objects.filter(poster=poster).exists())

    def test_redirect_counts_located_poster_and_redirects_to_destination(self):
        poster = PosterCampaign.objects.create(
            label="Test poster",
            destination_url="https://example.com/landing",
            first_scan_latitude=43.472285,
            first_scan_longitude=-80.544858,
        )

        response = self.client.get(f"/api/posters/{poster.id}/redirect/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "https://example.com/landing")
        poster.refresh_from_db()
        self.assertEqual(poster.scan_count, 1)
        self.assertEqual(PosterScan.objects.filter(poster=poster).count(), 1)
