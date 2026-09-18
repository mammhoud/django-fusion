"""Tenancy helpers — one source of truth for workspace scoping.

``auth.User`` remains the account (django-fusion references it directly), so the
workspace boundary lives on the one-to-one ``UserProfile``. Every read/write
path resolves the caller's workspace through ``current_workspace_id`` so a
cloud edition never leaks one tenant's records to another.

The convention matches the render-first screens already shipped: scope by
``workspace_id`` when it is known, and leave the queryset unscoped only for
callers that genuinely have no workspace (unauthenticated local-dev roads and
the super-admin seed path).
"""
from __future__ import annotations


def current_workspace_id(request) -> int | None:
    """Return the authenticated caller's workspace id, or ``None``."""
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    profile = getattr(user, "profile", None)
    return getattr(profile, "workspace_id", None)
