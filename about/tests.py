from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Person


class PersonListTests(APITestCase):
    """Checks the public people endpoint: filtering, hiding, ordering."""

    def setUp(self):
        Person.objects.create(
            name="Fr. A", role="Parish Priest",
            group=Person.Group.PASTORAL, category=Person.Category.CLERGY,
            role_type=Person.RoleType.PARISH_PRIEST, display_order=2,
        )
        Person.objects.create(
            name="Fr. B", role="Assistant Priest",
            group=Person.Group.PASTORAL, category=Person.Category.CLERGY,
            role_type=Person.RoleType.ASSISTANT_PRIEST, display_order=1,
        )
        Person.objects.create(
            name="Mrs C", role="Church Secretary",
            group=Person.Group.OFFICIAL, category=Person.Category.OFFICIAL,
            phone="000-000-0000",
        )
        Person.objects.create(
            name="Hidden Person", role="Priest",
            group=Person.Group.PASTORAL, category=Person.Category.CLERGY,
            is_active=False,
        )
        self.url = reverse("person-list")

    def names(self, response):
        return [person["name"] for person in response.data["results"]]

    def test_public_access_without_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_inactive_people_are_hidden(self):
        response = self.client.get(self.url)
        self.assertNotIn("Hidden Person", self.names(response))

    def test_filter_pastoral(self):
        response = self.client.get(self.url, {"group": "pastoral"})
        self.assertEqual(sorted(self.names(response)), ["Fr. A", "Fr. B"])

    def test_filter_official(self):
        response = self.client.get(self.url, {"group": "official"})
        self.assertEqual(self.names(response), ["Mrs C"])

    def test_display_order_is_respected(self):
        response = self.client.get(self.url, {"group": "pastoral"})
        self.assertEqual(self.names(response), ["Fr. B", "Fr. A"])

    def test_missing_photo_is_null(self):
        response = self.client.get(self.url, {"group": "official"})
        self.assertIsNone(response.data["results"][0]["photo"])

    def test_all_records_fit_in_one_response(self):
        Person.objects.bulk_create([
            Person(
                name=f"Placeholder {index}", role="Sample role",
                category=Person.Category.OFFICIAL,
            )
            for index in range(95)
        ])
        response = self.client.get(self.url)
        self.assertEqual(response.data["count"], 98)
        self.assertIsNone(response.data["next"])
        self.assertEqual(len(response.data["results"]), 98)

    def test_response_fields_are_exact(self):
        response = self.client.get(self.url)
        self.assertEqual(
            set(response.data["results"][0]),
            {"id", "name", "category", "role_type", "role", "badge",
             "society_code", "bio", "phone", "photo", "display_order"},
        )

    def test_public_list_is_ordered_by_display_order_then_id(self):
        response = self.client.get(self.url)
        self.assertEqual(self.names(response), ["Mrs C", "Fr. B", "Fr. A"])

    def test_public_api_rejects_writes(self):
        self.assertEqual(self.client.post(self.url, {}).status_code, 405)
        self.assertEqual(self.client.put(self.url, {}).status_code, 405)
        self.assertEqual(self.client.delete(self.url).status_code, 405)


class PersonValidationTests(APITestCase):
    def test_society_code_is_rejected_for_clergy(self):
        person = Person(
            name="Sample person", role="Sample role",
            category=Person.Category.CLERGY, society_code="SAMPLE",
        )
        with self.assertRaises(ValidationError):
            person.full_clean()
