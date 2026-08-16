from django.utils.translation import gettext_lazy as _

from apps.pages.accounts.models import Event

from .base import BaseIndexPage


class EventPage(BaseIndexPage):
    """A Wagtail page displaying a list of events."""

    # CTC-only template — see `projects/fusion-cms/templates/events/event_page.html`.
    template = "events/event_page.html"

    class Meta:
        verbose_name = _("Events Page")
        verbose_name_plural = _("Events Pages")

    def get_listed_items(self):
        """Return the Event queryset for pagination via BaseIndexPage.

        Replaces the previous ``get_context()`` override that injected a
        raw ``events`` queryset.  ``get_listed_items()`` lets
        ``BaseIndexPage.get_context()`` paginate the data naturally into
        ``page_items`` — which ``events/includes/events_grid.html`` now
        iterates over.

        Mirrors ``plugins/urls.py EventListView`` queryset so /events/
        renders identically through the Wagtail page or the plugin URL.
        """
        return Event.objects.filter(
            is_active=True, is_visible=True
        ).order_by("start_date", "title")
