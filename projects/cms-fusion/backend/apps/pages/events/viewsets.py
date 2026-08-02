"""
EventViewset for fusion-cms.com
=================================

Routable ModelViewset for Events management using django_fusion.
Registered in ``apps.pages.events.application.EventsApp.viewsets``.
Events are public content (list/detail) with staff-only write.

Usage::

    from apps.pages.events.viewsets import EventViewset
    # Register in apps/pages/events/application.py → EventsApp.viewsets
"""

from __future__ import annotations

from django_fusion.routes.models.crud import ModelViewset


class EventViewset(ModelViewset):
    """
    Full CRUD interface for events.

    Generates:
      GET  /events/              → list
      GET  /events/add/          → create form
      GET  /events/<pk>/detail/  → detail
      GET  /events/<pk>/change/  → update form
      GET  /events/<pk>/delete/  → delete confirm
    """

    icon = "date"

    @property
    def model(self):
        from apps.pages.accounts.models import Event
        return Event

    list_columns = ("title", "event_type", "start_date", "end_date", "location", "is_active")
    list_filter_fields = ("event_type", "is_active")
    list_search_fields = ("title", "description", "location")

    def has_view_permission(self, user, obj=None):
        return True  # Public list/detail

    def has_add_permission(self, user):
        return user.is_staff

    def has_change_permission(self, user, obj=None):
        return user.is_staff

    def has_delete_permission(self, user, obj=None):
        return user.is_staff


__all__ = ["EventViewset"]