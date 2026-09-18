"""Wagtail snippet registration for the handlers app."""

from wagtail.snippets.models import register_snippet

from apps.handlers.snippets.manage.event_translations import EventTranslationViewSet

register_snippet(EventTranslationViewSet)
