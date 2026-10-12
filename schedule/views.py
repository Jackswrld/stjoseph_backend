from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import ScheduleEntry
from .serializers import ScheduleEntrySerializer


class ScheduleListView(ListAPIView):
    queryset = ScheduleEntry.objects.filter(is_active=True)
    serializer_class = ScheduleEntrySerializer
    permission_classes = [AllowAny]
    pagination_class = None