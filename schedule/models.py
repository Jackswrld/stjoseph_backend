from django.db import models


class ScheduleEntry(models.Model):
    class Category(models.TextChoices):
        MASS = "mass", "Mass"
        ADORATION = "adoration", "Chapel of Adoration"
        CONFESSION = "confession", "Confession"
        SICK_COMMUNION = "sick_communion", "Communion of the sick/aged"
        BAPTISM = "baptism", "Baptism"
        CLASS = "class", "Classes (catechism, RCIA, Bible study, marriage)"
        OFFICE = "office", "Office and library"

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    class WeekOfMonth(models.IntegerChoices):
        FIRST = 1, "1st"
        SECOND = 2, "2nd"
        THIRD = 3, "3rd"
        FOURTH = 4, "4th"
        LAST = -1, "Last"

    category = models.CharField(max_length=20, choices=Category.choices)
    title = models.CharField(max_length=100)  # e.g. "Morning Mass"
    day_of_week = models.IntegerField(choices=Weekday.choices)
    week_of_month = models.IntegerField(
        choices=WeekOfMonth.choices, null=True, blank=True
    )  # empty = every week
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)  # empty = no end time
    note = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]
        verbose_name_plural = "schedule entries"

    def __str__(self):
        return f"{self.title} - {self.get_day_of_week_display()} {self.start_time:%H:%M}"