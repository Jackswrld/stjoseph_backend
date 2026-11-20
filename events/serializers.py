from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import (
    Event,
    EventGuest,
    EventHighlight,
    EventProgrammeItem,
    EventTeamMember,
)


class EventListSerializer(serializers.ModelSerializer):
    """Slim JSON for the cards. Only what a card shows."""

    # is_all_day is a property on the model, not a database column,
    # so we declare it here to include it in the JSON.
    is_all_day = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "slug",
            "date",
            "start_time",
            "end_time",
            "is_all_day",
            "location",
            "summary",
            "image",
        ]


class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventHighlight
        fields = ["label", "icon"]


class ProgrammeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventProgrammeItem
        fields = ["time", "title"]


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTeamMember
        fields = ["role", "name"]


class TeamSerializer(serializers.Serializer):
    """Describes the shape of "team" for the API docs only."""

    name = serializers.CharField()
    image = serializers.URLField(allow_null=True)
    members = TeamMemberSerializer(many=True)


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventGuest
        fields = ["name", "subtitle", "photo"]


class EventDetailSerializer(serializers.ModelSerializer):
    """Full JSON for the View Details modal."""

    is_all_day = serializers.BooleanField(read_only=True)
    # These names are the related_name values from models.py.
    highlights = HighlightSerializer(many=True, read_only=True)
    programme = ProgrammeItemSerializer(many=True, read_only=True)
    guests = GuestSerializer(many=True, read_only=True)
    # team is built by hand: the database has team_name, team_image and
    # team_members as separate pieces, but the JSON groups them together.
    team = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "slug",
            "badge",
            "tagline",
            "date",
            "start_time",
            "end_time",
            "is_all_day",
            "location",
            "image",
            "banner_image",
            "description",
            "highlights",
            "programme",
            "team",
            "guests",
            "important_info",
        ]

    @extend_schema_field(TeamSerializer)
    def get_team(self, obj):
        return {
            "name": obj.team_name,
            # With Cloudinary storage, .url is already a full https URL.
            "image": obj.team_image.url if obj.team_image else None,
            "members": TeamMemberSerializer(obj.team_members.all(), many=True).data,
        }