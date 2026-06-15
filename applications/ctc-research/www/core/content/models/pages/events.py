from django.utils.translation import gettext_lazy as _

from .base import BaseIndexPage


class EventPage(BaseIndexPage):
    """A Wagtail page displaying a list of events."""

    template = "base_page.html"
    template_name = "events/main.html"
    fragment_name = "events.main"
    page_title = _("Events Page")

    class Meta:
        verbose_name = _("Events Page")
        verbose_name_plural = _("Events Pages")

    # def get_listed_items(self):
    #     return Events.objects.filter(is_active=True).order_by("name")
