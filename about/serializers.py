from rest_framework import serializers

from .models import Person


class PersonSerializer(serializers.ModelSerializer):
    """Turns a Person into JSON for the About page."""

    class Meta:
        model = Person
        fields = [
            "id", "name", "category", "role_type", "role", "badge",
            "society_code", "bio", "phone", "photo", "display_order",
        ]
