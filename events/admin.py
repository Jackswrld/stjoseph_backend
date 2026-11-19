from django.contrib import admin

from .models import (
    Event,
    EventGuest,
    EventHighlight,
    EventProgrammeItem,
    EventTeamMember,
)


class EventHighlightInline(admin.TabularInline):
    model = EventHighlight
    extra = 1


class EventProgrammeItemInline(admin.TabularInline):
    model = EventProgrammeItem
    extra = 1


class EventTeamMemberInline(admin.TabularInline):
    model = EventTeamMember
    extra = 1


class EventGuestInline(admin.TabularInline):
    model = EventGuest
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "start_time", "location", "is_published")
    list_filter = ("is_published", "date")
    search_fields = ("title", "location")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        EventHighlightInline,
        EventProgrammeItemInline,
        EventTeamMemberInline,
        EventGuestInline,
    ]