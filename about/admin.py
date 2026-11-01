from django.contrib import admin

from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """How people are listed and edited in Django admin."""

    list_display = ("name", "category", "role", "display_order")
    list_filter = ("category",)
    search_fields = ("name", "role")
    list_editable = ("display_order",)
