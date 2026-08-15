"""Template context helpers shared by the render-first Loop-CRM shells.

``workspace_id`` is the single value the frontend needs to open the
workspace-scoped Server-Sent Events stream, so it is exposed here rather than
duplicated across every view's ``get_context_data``.
"""
from __future__ import annotations

from .tenancy import current_workspace_id


def workspace_id(request):
    """Return ``{"workspace_id": int | None}`` for the current request."""
    return {"workspace_id": current_workspace_id(request)}
