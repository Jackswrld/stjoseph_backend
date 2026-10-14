from datetime import time

from django.urls import reverse
from rest_framework.test import APITestCase

from .models import ScheduleEntry


class ScheduleListTests(APITestCase):
    def setUp(self):
        # Runs before every test. Creates the same starting data each time.
        self.url = reverse("schedule-list")
        self.sunday = ScheduleEntry.objects.create(
            category=ScheduleEntry.Category.MASS,
            title="Second Mass",
            day_of_week=ScheduleEntry.Weekday.SUNDAY,
            start_time=time(9, 0),
        )
        self.monday = ScheduleEntry.objects.create(
            category=ScheduleEntry.Category.MASS,
            title="Morning Mass",
            day_of_week=ScheduleEntry.Weekday.MONDAY,
            start_time=time(6, 30),
        )

    def test_returns_200_and_a_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_hides_inactive_entries(self):
        self.monday.is_active = False
        self.monday.save()
        response = self.client.get(self.url)
        titles = [item["title"] for item in response.json()]
        self.assertEqual(titles, ["Second Mass"])

    def test_entries_are_ordered_by_day_then_time(self):
        response = self.client.get(self.url)
        days = [item["day_of_week"] for item in response.json()]
        self.assertEqual(days, [0, 6])  # Monday first, Sunday last

    def test_response_shape_matches_the_contract(self):
        response = self.client.get(self.url)
        item = response.json()[0]  # the Monday entry
        self.assertEqual(
            set(item.keys()),
            {
                "id", "category", "category_display", "title",
                "day_of_week", "day_display", "week_of_month",
                "week_display", "start_time", "end_time", "note",
            },
        )
        self.assertEqual(item["day_display"], "Monday")
        self.assertEqual(item["start_time"], "06:30:00")
        self.assertIsNone(item["end_time"])
        self.assertIsNone(item["week_of_month"])
        self.assertIsNone(item["week_display"])

    def test_write_methods_are_not_allowed(self):
        response = self.client.post(self.url, {"title": "Hacked"})
        self.assertEqual(response.status_code, 405)  # Method Not Allowed