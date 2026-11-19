from django.db.models import F
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

from .models import Event
from .serializers import EventDetailSerializer, EventListSerializer


class EventPagination(PageNumberPagination):
    """12 events per page (the design is a 3-column grid)."""

    page_size = 12


class EventListView(generics.ListAPIView):
    """GET /api/v1/events/?when=upcoming|past|all  (default: upcoming)."""

    serializer_class = EventListSerializer
    pagination_class = EventPagination

    def get_queryset(self):
        when = self.request.query_params.get("when", "upcoming")
        # localdate() uses TIME_ZONE (Africa/Lagos), not UTC.
        today = timezone.localdate()
        events = Event.objects.filter(is_published=True)

        if when == "upcoming":
            return events.filter(date__gte=today)
        if when == "past":
            # Most recent first. nulls_last keeps all-day events after
            # timed ones on the same date.
            return events.filter(date__lt=today).order_by(
                "-date", F("start_time").desc(nulls_last=True)
            )
        if when == "all":
            return events
        raise ValidationError({"when": "Use one of: upcoming, past, all."})


class EventDetailView(generics.RetrieveAPIView):
    """GET /api/v1/events/<slug>/ : one published event, past or future."""

    serializer_class = EventDetailSerializer
    lookup_field = "slug"
    # prefetch_related loads the 4 related tables in 4 extra queries in
    # total, instead of extra queries for every row.
    queryset = Event.objects.filter(is_published=True).prefetch_related(
        "highlights", "programme", "team_members", "guests"
    )