from pathlib import PurePosixPath
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from datetime import date
from gallery.models import GalleryCategory, GalleryImage


CATEGORIES = [
    ("Mass & Sacraments", "mass-sacraments"),
    ("Church Events", "church-events"),
    ("Parish Activities", "parish-activities"),
    ("Societies", "societies"),
    ("Community Service", "community-service"),
    ("Special Occasions", "special-occasions"),
]

PLACEHOLDERS = [
    {
        "title": "Sunday Mass",
        "category_slug": "mass-sacraments",
        "date_taken": date(2025, 8, 24),
        "image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/de/Beautiful_altar_Easter.jpg/1280px-Beautiful_altar_Easter.jpg",
    },
    {
        "title": "Parish Thanksgiving",
        "category_slug": "church-events",
        "date_taken": date(2025, 8, 17),
        "image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/03/Cathedral_Harvest_of_Praise.jpg/1280px-Cathedral_Harvest_of_Praise.jpg",
    },
    {
        "title": "Catechism Class",
        "category_slug": "parish-activities",
        "date_taken": date(2025, 8, 10),
        "image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/58/Catechism_Class_in_the_Catholic_Church.jpg/1280px-Catechism_Class_in_the_Catholic_Church.jpg",
    },
    {
        "title": "Altar Servers",
        "category_slug": "societies",
        "date_taken": date(2025, 8, 3),
        "image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d5/Catholic_mass_servant_at_good_Friday_procession_in_Uniport.jpg/1280px-Catholic_mass_servant_at_good_Friday_procession_in_Uniport.jpg",
    },
    {
        "title": "Palm Sunday",
        "category_slug": "special-occasions",
        "date_taken": date(2025, 7, 27),
        "image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/69/Palm_Sunday_Celebration.jpg/1280px-Palm_Sunday_Celebration.jpg",
    },
]


class Command(BaseCommand):
    help = "Load gallery categories and optional placeholder images"

    def add_arguments(self, parser):
        # Register the optional placeholder creation and cleanup flags.
        parser.add_argument(
            "--placeholders",
            action="store_true",
            help="Download and create configured test placeholder images",
        )
        parser.add_argument(
            "--clear-placeholders",
            action="store_true",
            help="Delete gallery image records titled with the TEST prefix",
        )

    def handle(self, *args, **options):
        # Ensure the standard gallery categories exist, then apply requested actions.
        for order, (name, slug) in enumerate(CATEGORIES, start=1):
            GalleryCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "order": order},
            )

        if options["clear_placeholders"]:
            self.clear_placeholders()
        if options["placeholders"]:
            self.create_placeholders()

    def clear_placeholders(self):
        # Delete placeholder rows and remind operators to remove remote files.
        deleted, _ = GalleryImage.objects.filter(title__startswith="TEST - ").delete()
        self.stdout.write(f"Deleted {deleted} placeholder image record(s).")
        self.stdout.write(
            "Reminder: delete the corresponding files in Cloudinary manually."
        )

    def create_placeholders(self):
        # Download each configured image and continue after individual failures.
        for entry in PLACEHOLDERS:
            title = f"TEST - {entry['title']}"
            if GalleryImage.objects.filter(title=title).exists():
                self.stdout.write(f"Skipped existing placeholder: {title}")
                continue

            try:
                response = requests.get(
                    entry["image_url"],
                    timeout=30,
                    headers={"User-Agent": "StJosephGallerySeed/1.0 (parish website)"},
                )
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "").lower()
                if not content_type.startswith("image/"):
                    raise ValueError(
                        "expected image content, received "
                        f"{content_type or 'no content type'}"
                    )

                category = GalleryCategory.objects.get(slug=entry["category_slug"])
                image = GalleryImage(
                    title=title,
                    category=category,
                    date_taken=entry["date_taken"],
                )
                path = PurePosixPath(urlparse(entry["image_url"]).path)
                suffix = path.suffix or ".jpg"
                filename = f"{slugify(title) or 'placeholder'}{suffix}"
                image.image.save(filename, ContentFile(response.content), save=True)
                self.stdout.write(f"Created placeholder: {title}")
            except Exception as exc:
                self.stderr.write(f"Failed placeholder {title}: {exc}")
