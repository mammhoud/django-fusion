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

from django_fusion.routes.core.sites import Application
from django_fusion.routes.core.base import viewprop


class AccountsApp(Application):
    """Accounts — profiles, auth, and shared accounts content."""

    title = "Accounts"
    icon = "account_circle"
    app_name = "accounts"

    @viewprop
    def viewsets(self):
        # Register accounts-specific viewsets here (profiles, auth, etc.)
        return []

    def has_view_permission(self, user, obj=None):
        return True  # Public


__all__ = ["AccountsApp"]