from django.utils.translation import gettext_lazy as _

from www.apps.models import Event

from ..base import BaseSnippetViewSet


class EventViewSet(BaseSnippetViewSet):
    """Admin interface for managing Events."""

    model = Event
    menu_label = _("Events")
    icon = "date"
    menu_order = 180
    search_fields = ["title", "description", "location"]
    ordering = ["start_date"]

    # ======================
    # TABLE CONFIGURATION
    # ======================
    list_display = [
        "title",
        "event_type",
        "start_date",
        "end_date",
        # "is_active",
    ]
    list_filter = ["event_type"]
    list_export = ["title", "event_type", "start_date", "end_date", "location", "tags"]
    csv_filename = "events.csv"

    # ======================
    # DISPLAY HELPERS
    # ======================
    @staticmethod
    def event_type_display(obj):
        """Display human-readable event type with icon."""
        icons = {
            "workshop": "🛠️",
            "seminar": "🎤",
            "conference": "🏛️",
            "webinar": "💻",
            "meetup": "🤝",
            "other": "📌",
        }
        return f"{icons.get(obj.event_type, '📌')} {obj.get_event_type_display()}"
    event_type_display.short_description = _("Type")

    @staticmethod
    def is_active_display(obj):
        """Display active/inactive status."""
        return "🟢 Active" if obj.is_active else "🔴 Inactive"
    is_active_display.short_description = _("Status")
