from rest_framework import serializers

from .models import ScheduleEntry


class ScheduleEntrySerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    day_display = serializers.CharField(
        source="get_day_of_week_display", read_only=True
    )
    week_display = serializers.CharField(
        source="get_week_of_month_display", read_only=True
    )

    class Meta:
        model = ScheduleEntry
        fields = [
            "id",
            "category",
            "category_display",
            "title",
            "day_of_week",
            "day_display",
            "week_of_month",
            "week_display",
            "start_time",
            "end_time",
            "note",
        ]