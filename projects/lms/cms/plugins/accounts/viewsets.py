"""
Events Viewset for ctc-research.com
=====================================

Routable ModelViewset for Events management using django_fusion.
Registered in www/projects/routes.py → site viewsets.

Usage::

    from plugins.accounts.viewsets import EventViewset
    # Register in apps/projects/routes.py → BlogApp.viewsets or Site.viewsets
"""

from __future__ import annotations

from django_fusion.routes import ModelViewset


class EventViewset(ModelViewset):
    """
    Full CRUD interface for events.

    Generates:
      GET  /osoul/events/              → list
      GET  /osoul/events/add/          → create form
      GET  /osoul/events/<pk>/detail/  → detail
      GET  /osoul/events/<pk>/change/  → update form
      GET  /osoul/events/<pk>/delete/  → delete confirm
    """

    icon = "date"

    @property
    def model(self):
        from plugins.accounts.models import Event
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
