from django.contrib import admin

from .models import ScheduleEntry


@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "day_of_week",
        "week_of_month",
        "start_time",
        "end_time",
        "is_active",
    )
    list_filter = ("category", "day_of_week", "is_active")
    search_fields = ("title",)