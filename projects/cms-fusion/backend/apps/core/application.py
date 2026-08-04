"""
Core Application for fusion-cms.com
=====================================

Defines the ``CoreApp`` Application for cross-cutting fragment components
that don't belong to a single app — CMS head content injection, checkout
stubs, and other shared utilities.

Fragment components are registered in their related app's Application
viewsets.  Only truly cross-cutting fragments live here.

Usage (in core/routes.py)::

    from apps.core.application import CoreApp

    site = Site(title="Fusion CMS", viewsets=[LMSApp(), BlogApp(), CoreApp()])
"""

from __future__ import annotations

from django_fusion.routes.core.sites import Application
from django_fusion.routes.core.base import viewprop


class CoreApp(Application):
    """Cross-cutting shared fragments — CMS head, checkout, etc.

    Inherits ``NotificationMixin`` from ``Application`` (merged from
    ``PageHandler``), so child ``RoutableComponent`` views under this
    app automatically get ``add_success()``, ``add_error()``,
    ``show_notification()``, and SSE streaming without importing
    ``NotificationMixin`` separately.
    """

    title = "Core"
    icon = "widgets"
    app_name = "core"

    @viewprop
    def viewsets(self):
        from apps.core.site.components import CMSHeadContentFragment, CheckoutFragment
        return [
            CMSHeadContentFragment(),
            CheckoutFragment(),
        ]

    def has_view_permission(self, user, obj=None):
        return True  # Public


__all__ = ["CoreApp"]