from django.utils.translation import gettext_lazy as _

from plugins.accounts.models import Event

from core.pages_base import BaseIndexPage


class EventPage(BaseIndexPage):
    """A Wagtail page displaying a paginated list of events."""

    template = "events/event_page.html"

    class Meta:
        verbose_name = _("Events Page")
        verbose_name_plural = _("Events Pages")

    def get_listed_items(self):
        """Return the Event queryset for pagination via BaseIndexPage.

        Replaces the previous Django ``EventListView`` queryset injection
        with ``BaseIndexPage`` pagination.  ``page_items`` is populated by
        ``BaseIndexPage.get_context()`` — the grid template iterates over
        ``page_items`` instead of ``events``.
        """
        return Event.objects.filter(
            is_active=True, is_visible=True
        ).order_by("start_date", "title")

    def get_context(self, request, *args, **kwargs):
        """Extend the paginated context with ``page_title`` for VResume's chrome."""
        context = super().get_context(request, *args, **kwargs)
        context["page_title"] = self.title
        return context
