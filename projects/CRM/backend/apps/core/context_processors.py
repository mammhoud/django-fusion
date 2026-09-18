"""Template context helpers shared by the render-first Loop-CRM shells.

``workspace_id`` is the single value the frontend needs to open the
workspace-scoped Server-Sent Events stream, so it is exposed here rather than
duplicated across every view's ``get_context_data``.

``demo_state`` surfaces the demo credentials to the login page ONLY while
``DEMO_MODE`` is enabled; otherwise every value is empty so a production
deployment never leaks demo passwords.
"""
from __future__ import annotations

from django.conf import settings

from .demo import DEMO_EMAIL, DEMO_PASSWORD
from .tenancy import current_workspace_id


def workspace_id(request):
    """Return ``{"workspace_id": int | None}`` for the current request."""
    return {"workspace_id": current_workspace_id(request)}


def demo_state(request):
    """Return demo-mode flags + credentials for templates (empty when disabled)."""
    if settings.DEMO_MODE:
        return {
            "demo_mode": True,
            "demo_email": DEMO_EMAIL,
            "demo_password": DEMO_PASSWORD,
        }
    return {"demo_mode": False, "demo_email": "", "demo_password": ""}
