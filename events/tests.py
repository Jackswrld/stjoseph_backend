import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from rest_framework.test import APIClient

from .models import (
    Event,
    EventGuest,
    EventHighlight,
    EventProgrammeItem,
    EventTeamMember,
)

# NOTE: these tests never create images, so nothing is uploaded to Cloudinary.


def make_event(title, days=1, start=None, end=None, published=True, **extra):
    """Create an event `days` from today (negative = past). Today is Lagos time."""
    return Event.objects.create(
        title=title,
        slug=slugify(title),
        date=timezone.localdate() + datetime.timedelta(days=days),
        start_time=start,
        end_time=end,
        location="Parish Hall",
        summary="A short summary.",
        is_published=published,
        **extra,
    )


def titles(response):
    """The event titles in a list response, in order."""
    return [item["title"] for item in response.data["results"]]


class EventModelTests(TestCase):
    def test_is_all_day_depends_on_start_time(self):
        self.assertTrue(Event(title="A").is_all_day)
        self.assertFalse(Event(title="B", start_time=datetime.time(9, 0)).is_all_day)

    def test_end_time_without_start_time_is_rejected(self):
        event = Event(title="A", end_time=datetime.time(10, 0))
        with self.assertRaises(ValidationError):
            event.clean()

    def test_end_time_before_start_time_is_rejected(self):
        event = Event(
            title="A", start_time=datetime.time(10, 0), end_time=datetime.time(9, 0)
        )
        with self.assertRaises(ValidationError):
            event.clean()

    def test_valid_times_pass(self):
        event = Event(
            title="A", start_time=datetime.time(9, 0), end_time=datetime.time(10, 0)
        )
        event.clean()  # must not raise


class SettingsTests(TestCase):
    def test_timezone_is_lagos(self):
        # "Today" for upcoming events is computed from this setting.
        self.assertEqual(settings.TIME_ZONE, "Africa/Lagos")


class EventListTests(TestCase):
    def setUp(self):
        self.client = APIClient()  # anonymous: no login, like the real frontend
        self.url = reverse("event-list")

    def test_anonymous_visitor_can_read(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_default_shows_only_upcoming_published(self):
        make_event("Future", days=5)
        make_event("Past", days=-5)
        make_event("Draft", days=5, published=False)
        response = self.client.get(self.url)
        self.assertEqual(titles(response), ["Future"])

    def test_event_today_is_upcoming_not_past(self):
        make_event("Today", days=0)
        self.assertEqual(titles(self.client.get(self.url)), ["Today"])
        self.assertEqual(titles(self.client.get(self.url, {"when": "past"})), [])

    def test_upcoming_order_soonest_first_timed_before_all_day(self):
        make_event("Later", days=10, start=datetime.time(9, 0))
        make_event("All day", days=3)  # no times
        make_event("Morning", days=3, start=datetime.time(9, 0))
        make_event("Evening", days=3, start=datetime.time(18, 0))
        response = self.client.get(self.url)
        self.assertEqual(titles(response), ["Morning", "Evening", "All day", "Later"])

    def test_past_shows_only_past_most_recent_first(self):
        make_event("Old", days=-10)
        make_event("Recent", days=-3)
        make_event("Future", days=3)
        make_event("Past draft", days=-3, published=False)
        response = self.client.get(self.url, {"when": "past"})
        self.assertEqual(titles(response), ["Recent", "Old"])

    def test_all_shows_everything_published(self):
        make_event("Old", days=-10)
        make_event("Future", days=3)
        make_event("Draft", days=3, published=False)
        response = self.client.get(self.url, {"when": "all"})
        self.assertEqual(titles(response), ["Old", "Future"])

    def test_invalid_when_returns_400(self):
        response = self.client.get(self.url, {"when": "banana"})
        self.assertEqual(response.status_code, 400)

    def test_list_returns_only_the_slim_fields(self):
        make_event("Future", days=3, description="Long text that cards must not get.")
        item = self.client.get(self.url).data["results"][0]
        self.assertEqual(
            set(item.keys()),
            {
                "id", "title", "slug", "date", "start_time", "end_time",
                "is_all_day", "location", "summary", "image",
            },
        )

    def test_all_day_event_has_null_times(self):
        make_event("All day", days=3)
        item = self.client.get(self.url).data["results"][0]
        self.assertIsNone(item["start_time"])
        self.assertIsNone(item["end_time"])
        self.assertTrue(item["is_all_day"])
        self.assertIsNone(item["image"])

    def test_pagination_is_12_per_page(self):
        for number in range(13):
            make_event(f"Event {number:02d}", days=number + 1)
        response = self.client.get(self.url)
        self.assertEqual(response.data["count"], 13)
        self.assertEqual(len(response.data["results"]), 12)
        self.assertIsNotNone(response.data["next"])
        page_two = self.client.get(self.url, {"page": 2})
        self.assertEqual(len(page_two.data["results"]), 1)


class EventDetailTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def detail(self, slug):
        return self.client.get(reverse("event-detail", kwargs={"slug": slug}))

    def test_past_published_event_is_returned(self):
        make_event("Old event", days=-30)
        self.assertEqual(self.detail("old-event").status_code, 200)

    def test_unpublished_event_is_404(self):
        make_event("Secret", days=3, published=False)
        self.assertEqual(self.detail("secret").status_code, 404)

    def test_unknown_slug_is_404(self):
        self.assertEqual(self.detail("does-not-exist").status_code, 404)

    def test_event_without_modal_data_has_empty_sections(self):
        make_event("Plain", days=3)
        data = self.detail("plain").data
        self.assertEqual(data["highlights"], [])
        self.assertEqual(data["programme"], [])
        self.assertEqual(data["guests"], [])
        self.assertEqual(data["team"], {"name": "", "image": None, "members": []})
        self.assertEqual(data["badge"], "")
        self.assertEqual(data["important_info"], "")
        self.assertIsNone(data["banner_image"])

    def test_related_rows_come_back_in_the_right_order(self):
        event = make_event("Full", days=3, team_name="Committee")
        EventHighlight.objects.create(event=event, label="Second", order=2)
        EventHighlight.objects.create(event=event, label="First", order=1)
        # Created out of order on purpose: the API must sort by time.
        EventProgrammeItem.objects.create(
            event=event, time=datetime.time(11, 0), title="Late"
        )
        EventProgrammeItem.objects.create(
            event=event, time=datetime.time(9, 0), title="Early"
        )
        EventTeamMember.objects.create(
            event=event, role="Coordinator", name="Grace", order=1
        )
        EventGuest.objects.create(event=event, name="Guest Speaker", subtitle="TBA")

        data = self.detail("full").data
        self.assertEqual([h["label"] for h in data["highlights"]], ["First", "Second"])
        self.assertEqual([p["title"] for p in data["programme"]], ["Early", "Late"])
        self.assertEqual(data["programme"][0]["time"], "09:00:00")
        self.assertEqual(data["team"]["name"], "Committee")
        self.assertEqual(
            list(data["team"]["members"]), [{"role": "Coordinator", "name": "Grace"}]
        )
        self.assertIsNone(data["guests"][0]["photo"])

    def test_detail_uses_a_fixed_number_of_queries(self):
        event = make_event("Busy", days=3)
        for number in range(5):
            EventHighlight.objects.create(event=event, label=f"H{number}")
            EventGuest.objects.create(event=event, name=f"G{number}")
            EventTeamMember.objects.create(event=event, role="R", name=f"N{number}")
        # 1 query for the event + 4 prefetches. More rows must not add queries.
        with self.assertNumQueries(5):
            self.assertEqual(self.detail("busy").status_code, 200)