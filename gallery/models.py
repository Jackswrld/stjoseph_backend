from django.db import models


class GalleryCategory(models.Model):
    """A group of photos. Each category becomes a filter button on the Gallery page."""

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(
        max_length=60,
        unique=True,
        help_text="Used in URLs. Do not change it after the site is live.",
    )
    order = models.PositiveSmallIntegerField(
        default=0, help_text="Smaller numbers appear first."
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "gallery categories"

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    """One photo tile on the Gallery page."""

    title = models.CharField(max_length=120)
    image = models.ImageField(upload_to="gallery/")
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.PROTECT,
        related_name="images",
    )
    date_taken = models.DateField(help_text="Date of the event. Shown on the page.")
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Describes the photo for screen readers. Optional.",
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_taken", "-id"]

    def __str__(self):
        return f"{self.title} ({self.date_taken})"