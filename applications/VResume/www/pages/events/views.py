from django.http import Http404
from django.views.generic import DetailView

from wagtail.models import Page, Site


def event_list_view(request):
    """
    Serve the Wagtail EventPage by finding it in the page tree.

    Replaces the old Django ``EventListView``.  The ``EventPage``
    (``BaseIndexPage`` subclass) handles pagination via
    ``get_listed_items()`` and the grid template iterates over
    ``page_items``.
    """
    site = Site.find_for_request(request)
    if not site:
        raise Http404("No site configured")

    from pages.events.models import EventPage

    page = (
        Page.objects.child_of(site.root_page)
        .type(EventPage)
        .live()
        .first()
    )
    if not page:
        raise Http404("No events page found")

    return page.specific.serve(request)


class EventDetailView(DetailView):
    """Public event detail page using the shared Event content blocks."""

    template_name = "events/detail.html"
    context_object_name = "event"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        from plugins.accounts.models import Event

        return Event.objects.filter(is_active=True, is_visible=True)

    def get_object(self, queryset=None):
        if not self.kwargs.get(self.pk_url_kwarg):
            raise Http404("Event not found")
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"active_tab": "events", "page_title": self.object.title})
        return context
