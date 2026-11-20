from django.test import TestCase
from django.urls import reverse


class HealthTests(TestCase):
    def test_health_is_ok_and_does_not_touch_the_database(self):
        # assertNumQueries(0) fails if anyone later adds a database call here.
        with self.assertNumQueries(0):
            response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})