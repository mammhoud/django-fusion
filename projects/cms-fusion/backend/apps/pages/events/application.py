"""
Events Application for fusion-cms.com
============================================

Defines the ``EventsApp`` Application (routable-components hierarchy node)
for Event management.  Separated from ``accounts`` so that the events
module stands on its own and does not introduce cross-app imports in
other applications.

Usage (in core/routes.py)::

    from apps.pages.events.application import EventsApp

    site = Site(title="Fusion CMS", viewsets=[LMSApp(), BlogApp(), EventsApp(), CoreApp()])
"""

from __future__ import annotations

from django_fusion.routes.core.sites import Application
from django_fusion.routes.core.base import viewprop


class EventsApp(Application):
    """Events — public read, staff write."""

    title = "Events"
    icon = "date_range"
    app_name = "events"

    @viewprop
    def viewsets(self):
        from apps.pages.events.components import EventCreateFragment, EventListFragment
        from apps.pages.events.viewsets import EventViewset
        return [
            EventViewset(),
            EventListFragment(),
            EventCreateFragment(),
        ]

    def has_view_permission(self, user, obj=None):
        return True  # Public


__all__ = ["EventsApp"]