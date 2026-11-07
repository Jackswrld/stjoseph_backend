from datetime import date

from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import GalleryCategory, GalleryImage

# Tests must never upload to Cloudinary, so they use in-memory storage.
IN_MEMORY_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}


@override_settings(STORAGES=IN_MEMORY_STORAGES)
class GalleryApiTests(APITestCase):
    def setUp(self):
        # Two visible categories and one hidden one.
        self.mass = GalleryCategory.objects.create(
            name="Mass & Sacraments", slug="mass-sacraments", order=1
        )
        self.societies = GalleryCategory.objects.create(
            name="Societies", slug="societies", order=2
        )
        self.hidden = GalleryCategory.objects.create(
            name="Hidden", slug="hidden", order=3, is_active=False
        )

    def make_image(self, title, category, **extra):
        # Assigning a path string saves the row without uploading any file.
        extra.setdefault("date_taken", date(2025, 1, 1))
        return GalleryImage.objects.create(
            title=title, image=f"gallery/{title}.jpg", category=category, **extra
        )

    def test_categories_list_only_active_in_order(self):
        response = self.client.get(reverse("gallery-categories"))
        self.assertEqual(response.status_code, 200)
        names = [item["name"] for item in response.json()]
        self.assertEqual(names, ["Mass & Sacraments", "Societies"])

    def test_images_hide_unpublished(self):
        self.make_image("shown", self.mass)
        self.make_image("draft", self.mass, is_published=False)
        response = self.client.get(reverse("gallery-images"))
        titles = [item["title"] for item in response.json()["results"]]
        self.assertEqual(titles, ["shown"])

    def test_images_hide_inactive_category(self):
        self.make_image("in-hidden-category", self.hidden)
        response = self.client.get(reverse("gallery-images"))
        self.assertEqual(response.json()["count"], 0)

    def test_images_newest_event_first(self):
        self.make_image("old", self.mass, date_taken=date(2025, 1, 1))
        self.make_image("new", self.mass, date_taken=date(2025, 6, 1))
        response = self.client.get(reverse("gallery-images"))
        titles = [item["title"] for item in response.json()["results"]]
        self.assertEqual(titles, ["new", "old"])

    def test_filter_by_category_slug(self):
        self.make_image("mass-photo", self.mass)
        self.make_image("society-photo", self.societies)
        response = self.client.get(reverse("gallery-images"), {"category": "societies"})
        titles = [item["title"] for item in response.json()["results"]]
        self.assertEqual(titles, ["society-photo"])

    def test_page_size_is_eight(self):
        for number in range(9):
            self.make_image(f"photo-{number}", self.mass)
        response = self.client.get(reverse("gallery-images"))
        data = response.json()
        self.assertEqual(data["count"], 9)
        self.assertEqual(len(data["results"]), 8)
        self.assertIsNotNone(data["next"])

    def test_anonymous_users_cannot_write(self):
        response = self.client.post(reverse("gallery-images"), {"title": "x"})
        # DRF checks permissions before it checks the method, so this is 401 or 403, not 405.
        self.assertIn(response.status_code, (401, 403))