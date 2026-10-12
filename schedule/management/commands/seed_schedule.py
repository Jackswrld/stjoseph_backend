from datetime import time

from django.core.management.base import BaseCommand

from schedule.models import ScheduleEntry

C = ScheduleEntry.Category
D = ScheduleEntry.Weekday
W = ScheduleEntry.WeekOfMonth

MON_FRI = [D.MONDAY, D.TUESDAY, D.WEDNESDAY, D.THURSDAY, D.FRIDAY]
SAT_SUN = [D.SATURDAY, D.SUNDAY]

# (category, title, days, week_of_month, start_time, end_time)
ENTRIES = [
    # Sunday Masses
    (C.MASS, "First Mass", [D.SUNDAY], None, time(6, 30), None),
    (C.MASS, "Second Mass", [D.SUNDAY], None, time(9, 0), None),
    (C.MASS, "Evening Mass", [D.SUNDAY], None, time(18, 0), None),
    (C.MASS, "Children's Mass", [D.SUNDAY], None, time(9, 30), time(11, 0)),
    # Weekday Masses
    (C.MASS, "Morning Mass", MON_FRI, None, time(6, 30), None),
    (C.MASS, "Evening Mass", [D.TUESDAY, D.WEDNESDAY, D.THURSDAY, D.FRIDAY], None, time(18, 0), None),
    (C.MASS, "Saturday Mass", [D.SATURDAY], None, time(7, 0), None),
    # Office and library
    (C.OFFICE, "Office Hours", [D.MONDAY, D.TUESDAY, D.WEDNESDAY, D.THURSDAY], None, time(9, 0), time(13, 0)),
    (C.OFFICE, "Library", MON_FRI, None, time(9, 0), time(14, 0)),
    # Chapel of Adoration
    (C.ADORATION, "Exposition", MON_FRI, None, time(7, 15), time(21, 0)),
    (C.ADORATION, "Benediction", [D.THURSDAY], None, time(17, 30), None),
    # Sick and aged
    (C.SICK_COMMUNION, "Communion of the Sick/Aged", [D.THURSDAY, D.FRIDAY], None, time(9, 0), time(13, 0)),
    # Confession
    (C.CONFESSION, "Confession", [D.SATURDAY], None, time(17, 0), time(19, 0)),
    # Classes
    (C.CLASS, "Catechism", SAT_SUN, None, time(16, 0), time(18, 0)),
    (C.CLASS, "R.C.I.A", SAT_SUN, None, time(16, 0), None),
    (C.CLASS, "Bible Study Class", [D.WEDNESDAY], None, time(19, 15), None),
    (C.CLASS, "Marriage Classes", [D.SUNDAY], None, time(16, 0), time(18, 0)),
    # Baptism (monthly rules)
    (C.BAPTISM, "Infant Baptism Preparation", [D.SATURDAY], W.FIRST, time(16, 0), None),
    (C.BAPTISM, "Infant Baptism Preparation", [D.SATURDAY], W.SECOND, time(16, 0), None),
    (C.BAPTISM, "Baptism", [D.SATURDAY], W.LAST, time(11, 0), None),
]


class Command(BaseCommand):
    help = "Load the parish schedule into the database"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for category, title, days, week, start, end in ENTRIES:
            for day in days:
                _, created = ScheduleEntry.objects.update_or_create(
                    title=title,
                    day_of_week=day,
                    week_of_month=week,
                    defaults={
                        "category": category,
                        "start_time": start,
                        "end_time": end,
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Done: {created_count} created, {updated_count} updated")
        )