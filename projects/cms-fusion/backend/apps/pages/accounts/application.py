"""
Accounts Application for fusion-cms.com
=========================================

Defines the ``AccountsApp`` Application (routable-components hierarchy node)
for accounts-related content (profiles, auth, etc.).  Event management has
been moved to ``apps.pages.events.application.EventsApp``.

Kept in the accounts app so core routing only assembles the ``Site`` from
app-level Application classes.

Usage (in core/routes.py)::

    from apps.pages.accounts.application import AccountsApp

    site = Site(title="Fusion CMS", viewsets=[LMSApp(), BlogApp(), AccountsApp(), EventsApp(), CoreApp()])
"""

from __future__ import annotations

from typing import Any

from django_fusion.routes.core.sites import Application
from django_fusion.routes.core.base import viewprop


class AccountsApp(Application):
    """Accounts — profiles, auth, and shared accounts content.

    Inherits ``NotificationMixin`` from ``Application`` (merged from
    ``PageHandler``), so child ``RoutableComponent`` views (registration,
    password reset, profile updates) automatically get ``add_success()``,
    ``add_error()``, and SSE streaming for form feedback toasts.
    """

    title = "Accounts"
    icon = "account_circle"
    app_name = "accounts"

    @viewprop
    def viewsets(self):
        # Register accounts-specific viewsets here (profiles, auth, etc.)
        return []

    def application_context(self, request: Any) -> dict[str, Any]:
        """Inject account-level context."""
        user = getattr(request, "user", None)
        return {
            "accounts_title": self.title,
            "accounts_icon": self.icon,
            "is_authenticated": user.is_authenticated if user else False,
        }

    def has_view_permission(self, user, obj=None):
        return True  # Public


__all__ = ["AccountsApp"]