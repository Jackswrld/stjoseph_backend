from django.urls import path

from .views import GalleryCategoryListView, GalleryImageListView

urlpatterns = [
     path("categories/", GalleryCategoryListView.as_view(), name="gallery-categories"),
    path("images/", GalleryImageListView.as_view(), name="gallery-images"),
]