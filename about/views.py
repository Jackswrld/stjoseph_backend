from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from .models import Person
from .serializers import PersonSerializer


class PersonPagination(PageNumberPagination):
    page_size = 100


class PersonListView(ListAPIView):
    """Public list of active people for the About page. Supports ?group=pastoral or ?group=official."""

    queryset = Person.objects.filter(is_active=True)
    serializer_class = PersonSerializer
    permission_classes = [AllowAny]
    pagination_class = PersonPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["group"]
