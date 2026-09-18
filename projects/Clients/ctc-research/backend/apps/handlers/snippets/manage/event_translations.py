"""Snippet admin for EventTranslation overlays."""

from django.utils.translation import gettext_lazy as _

from apps.handlers.models.manage.event_translation import EventTranslation

from ..base import BaseSnippetViewSet


class EventTranslationViewSet(BaseSnippetViewSet):
    """Admin interface for managing Event translations."""

    model = EventTranslation
    menu_label = _("Event translations")
    icon = "doc-full-inverse"
    menu_order = 190
    search_fields = ["event__title", "title"]
    ordering = ["event_id", "language"]
    list_display = ["event", "language", "title", "updated_at"]
    list_filter = ["language"]
    list_export = ["event", "language", "title", "description", "location"]
    csv_filename = "event_translations.csv"
