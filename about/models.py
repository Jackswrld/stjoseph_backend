from django.db import models


class Person(models.Model):
    """A person shown on the About page (priest, catechist, or church official)."""

    class Group(models.TextChoices):
        PASTORAL = "pastoral", "Pastoral"
        OFFICIAL = "official", "Church official"

    class Category(models.TextChoices):
        CLERGY = "clergy", "Clergy"
        OFFICIAL = "official", "Official"
        SOCIETY_LEADER = "society_leader", "Society leader"

    class RoleType(models.TextChoices):
        PARISH_PRIEST = "parish_priest", "Parish priest"
        ASSISTANT_PRIEST = "assistant_priest", "Assistant priest"
        CATECHIST = "catechist", "Catechist"

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices)
    role_type = models.CharField(max_length=30, choices=RoleType.choices, blank=True)
    badge = models.CharField(max_length=40, blank=True)
    # Temporary. Will become a ForeignKey to Society when the Societies backend exists.
    society_code = models.CharField(max_length=10, blank=True)
    group = models.CharField(max_length=20, choices=Group.choices)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to="people/", blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name_plural = "people"

    def __str__(self):
        return f"{self.name} ({self.role})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.role_type and self.category != self.Category.CLERGY:
            errors["role_type"] = "Role type is only allowed for clergy."
        if self.society_code and self.category != self.Category.SOCIETY_LEADER:
            errors["society_code"] = "Society code is only allowed for society leaders."
        if errors:
            raise ValidationError(errors)

# Create your models here.
