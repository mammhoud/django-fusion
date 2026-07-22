"""
Shared helpers for bolt API handlers — image URL, user display name, pagination.
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


# ── Image URL helper ──


def get_image_url(image_field) -> str:
    """Extract absolute URL from a Wagtail / Django image FileField.

    Returns empty string if the field is None or has no file.
    """
    if image_field is None:
        return ""
    try:
        return image_field.file.url
    except Exception:
        pass
    try:
        return image_field.url
    except Exception:
        return ""


# ── User display name helper ──


def get_user_display_name(user) -> str:
    """Return the best display name for a User instance."""
    if user is None:
        return ""
    try:
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        if user.first_name:
            return user.first_name
        if user.get_full_name():
            return user.get_full_name()
        return user.username
    except Exception:
        return str(user)


# ── Pagination helper ──


def paginate_queryset(qs, request, default_per_page: int = 20):
    """Paginate a Django QuerySet using query params ``page`` and ``per_page``.

    Returns ``(items, pagination_dict)`` where ``items`` is the sliced
    QuerySet for the current page.
    """
    page = _int_param(request, "page", 1)
    per_page = _int_param(request, "per_page", default_per_page)
    total = qs.count()
    items = qs[(page - 1) * per_page : page * per_page]
    total_pages = max(1, (total + per_page - 1) // per_page)
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }
    return items, pagination


def _int_param(request, name: str, default: int) -> int:
    """Extract an integer query parameter, falling back to ``default``."""
    try:
        return int(request.GET.get(name, default))
    except (TypeError, ValueError):
        return default


# ── Request body parsing ──


def parse_body(request) -> dict[str, Any]:
    """Parse JSON request body to dict. Returns empty dict on failure."""
    try:
        return json.loads(request.body)
    except Exception:
        return {}


# ── Auth helper ──


def get_current_user(request):
    """Safely get the current user from a bolt request."""
    if hasattr(request, "user") and request.user and not request.user.is_anonymous:
        return request.user
    from www.auth import authenticate_request
    return authenticate_request(request)
