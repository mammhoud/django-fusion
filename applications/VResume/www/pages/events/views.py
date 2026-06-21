from django.http import Http404
from django.views.generic import DetailView, ListView


class EventListView(ListView):
    """Public event listing backed by the shared Event snippet model."""

    template_name = "events/main.html"
    context_object_name = "events"

    def get_queryset(self):
        from plugins.accounts.models import Event

        return Event.objects.filter(is_active=True, is_visible=True).order_by(
            "start_date", "title"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"active_tab": "events", "page_title": "Events"})
        return context


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
