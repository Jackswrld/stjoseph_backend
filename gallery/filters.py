from django_filters import rest_framework as filters

from .models import GalleryImage


class GalleryImageFilter(filters.FilterSet):
    """Lets the frontend ask for ?category=<slug>."""

    category = filters.CharFilter(field_name="category__slug")

    class Meta:
        model = GalleryImage
        fields = ["category"]