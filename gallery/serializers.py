from rest_framework import serializers

from .models import GalleryCategory, GalleryImage


class GalleryCategorySerializer(serializers.ModelSerializer):
    """Turns a category into JSON for the filter buttons."""

    class Meta:
        model = GalleryCategory
        fields = ["id", "name", "slug"]


class GalleryImageSerializer(serializers.ModelSerializer):
    """Turns one photo into JSON, with its category nested inside."""

    category = GalleryCategorySerializer(read_only=True)
    # The model field is "image", but the API contract calls it "image_url".
    image_url = serializers.ImageField(source="image", read_only=True)

    class Meta:
        model = GalleryImage
        fields = ["id", "title", "image_url", "date_taken", "alt_text", "category"]