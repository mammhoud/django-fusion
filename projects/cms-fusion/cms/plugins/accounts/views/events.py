"""Events views for ctc-research — public event listing and detail."""

from django.views.generic import DetailView, ListView


class EventListView(ListView):
    """Public event listing backed by the shared Event snippet model."""

    template_name = "events/events.html"
    context_object_name = "events"

    def get_queryset(self):
        from plugins.accounts.models import Event

        return Event.objects.filter(is_active=True, is_visible=True).order_by(
            "start_date", "title"
        )


class EventDetailView(DetailView):
    """Public event detail backed by the shared Event snippet model."""

    template_name = "events/detail.html"
    context_object_name = "event"

    def get_queryset(self):
        from plugins.accounts.models import Event

        return Event.objects.filter(is_active=True, is_visible=True)
