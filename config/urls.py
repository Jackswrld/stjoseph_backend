from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import health

urlpatterns = [
    path("", health, name="root"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("core.urls")),
     path("api/v1/schedule/", include("schedule.urls")),
     path("api/v1/health/", health, name="health"),
     path("api/v1/about/", include("about.urls")),
     path("api/v1/gallery/", include("gallery.urls")),
     path("api/v1/events/", include("events.urls")),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]