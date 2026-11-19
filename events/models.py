from django.core.exceptions import ValidationError
from django.db import models


class Event(models.Model):
    """One church event shown on the Events page."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    date = models.DateField()
    # Empty start_time means "All Day Event".
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    summary = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    # --- Modal (View Details) fields. All optional. ---
    # e.g. "Parish Event"
    badge = models.CharField(max_length=40, blank=True)
    # italic line under the title
    tagline = models.CharField(max_length=200, blank=True)
    banner_image = models.ImageField(
        upload_to="events/banners/", null=True, blank=True)
    # e.g. "Parish Events Committee"
    team_name = models.CharField(max_length=120, blank=True)
    team_image = models.ImageField(
        upload_to="events/teams/", null=True, blank=True)
    important_info = models.TextField(blank=True)
    image = models.ImageField(upload_to="events/", null=True, blank=True)
    # Staff can hide an event without deleting it.
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.title} ({self.date})"

    @property
    def is_all_day(self):
        return self.start_time is None

    def clean(self):
        # An end time without a start time makes no sense.
        if self.end_time and not self.start_time:
            raise ValidationError(
                "Set a start time before setting an end time.")
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

class EventHighlight(models.Model):
    """One item in "What to Expect". Staff pick an icon key from a dropdown."""

    class Icon(models.TextChoices):
        # The frontend maps each key to an icon. Unknown key = fallback icon.
        CHALICE = "chalice", "Chalice (Mass)"
        PROCESSION = "procession", "Procession"
        MUSIC = "music", "Music"
        FELLOWSHIP = "fellowship", "Fellowship"
        FOOD = "food", "Food"
        PRAYER = "prayer", "Prayer"
        BOOK = "book", "Bible / Reading"
        OTHER = "other", "Other"

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="highlights")
    label = models.CharField(max_length=60)
    icon = models.CharField(
        max_length=20, choices=Icon.choices, default=Icon.OTHER)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.label


class EventProgrammeItem(models.Model):
    """One row in "Programme of Activities"."""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="programme")
    time = models.TimeField()
    title = models.CharField(max_length=120)

    class Meta:
        ordering = ["time", "id"]

    def __str__(self):
        return f"{self.time} {self.title}"


class EventTeamMember(models.Model):
    """One person in the Organising Team list."""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="team_members")
    role = models.CharField(max_length=80)
    name = models.CharField(max_length=120)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.role}: {self.name}"


class EventGuest(models.Model):
    """One card in "Special Guests". Photo is optional."""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="guests")
    name = models.CharField(max_length=120)
    subtitle = models.CharField(
        max_length=120, blank=True)  # e.g. "Parish Priest"
    photo = models.ImageField(
        upload_to="events/guests/", null=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name
