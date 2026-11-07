from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from .filters import GalleryImageFilter
from .models import GalleryCategory, GalleryImage
from .serializers import GalleryCategorySerializer, GalleryImageSerializer


class GalleryPagination(PageNumberPagination):
    """The gallery shows 8 photos per page (the global default is 11)."""

    page_size = 8


class GalleryCategoryListView(generics.ListAPIView):
    """Active categories, in the order set in admin."""

    queryset = GalleryCategory.objects.filter(is_active=True)
    serializer_class = GalleryCategorySerializer
    pagination_class = None  # The buttons need the full list, not a page of it.


class GalleryImageListView(generics.ListAPIView):
    """Published photos, newest event first. Supports ?category=<slug>."""

    queryset = GalleryImage.objects.filter(
        is_published=True, category__is_active=True
    ).select_related("category")
    serializer_class = GalleryImageSerializer
    pagination_class = GalleryPagination
    filterset_class = GalleryImageFilter