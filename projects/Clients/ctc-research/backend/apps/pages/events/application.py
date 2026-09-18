"""
Events Application for precis-lms.com
============================================

Defines the ``EventsApp`` Application (routable-components hierarchy node)
for Event management.  Separated from ``accounts`` so that the events
module stands on its own and does not introduce cross-app imports in
other applications.

Usage (in core/routes.py)::

    from apps.pages.events.application import EventsApp

    module = Module(title="LMS Fusion", viewsets=[LMSApp(), BlogApp(), EventsApp(), CoreApp()])
"""

from __future__ import annotations

from typing import Any

from django_fusion.routes.core.base import viewprop
from django_fusion.routes.core.sites import Application


class EventsApp(Application):
    """Events — public read, staff write.

    Inherits ``NotificationMixin`` from ``Application`` (merged from
    ``PageHandler``), so child ``RoutableComponent`` views (create,
    delete, RSVP) automatically get ``add_success()`` and
    ``add_error()`` for confirmation toasts.
    """

    title = "Events"
    icon = "date_range"
    app_name = "events"

    # The public events grid is a Wagtail ``EventPage`` served at ``/events/``
    # (mirroring LMS). The inherited ``index_path`` would 302 ``/events/`` to
    # the staff-only routable EventViewset list (``/events/event/``), shadowing
    # the Wagtail page. ``index_path = None`` removes the inherited pattern
    # (ViewsetMeta treats ``None`` as "remove inherited pattern") so Wagtail
    # keeps serving the page while the HTMX action fragments
    # (``/events/list-fragment/``, ``/events/create-fragment/``) stay mounted.
    index_path = None

    @viewprop
    def viewsets(self):
        from apps.pages.events.components import EventCreateFragment, EventListFragment
        from apps.pages.events.viewsets import EventViewset
        return [
            EventViewset(),
            EventListFragment(),
            EventCreateFragment(),
        ]

    def application_context(self, request: Any) -> dict[str, Any]:
        """Inject event-level context."""
        user = getattr(request, "user", None)
        return {
            "events_title": self.title,
            "events_icon": self.icon,
            "can_manage_events": (
                user.is_authenticated and user.is_staff
                if user else False
            ),
        }

    def has_view_permission(self, user, obj=None):
        return True  # Public


__all__ = ["EventsApp"]