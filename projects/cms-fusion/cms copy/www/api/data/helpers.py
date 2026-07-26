"""
Shared helpers for data API handlers — image URL, user display name, pagination.
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

    Also handles plain lists (e.g. from fallback backends) gracefully.
    """
    page = _int_param(request, "page", 1)
    per_page = _int_param(request, "per_page", 0) or _int_param(
        request, "page_size", default_per_page
    )

    # Handle plain list/QuerySet generically
    if isinstance(qs, (list, tuple)):
        total = len(qs)
        items = qs[(page - 1) * per_page : page * per_page]
    else:
        try:
            total = qs.count()
            items = qs[(page - 1) * per_page : page * per_page]
        except Exception:
            total = 0
            items = []

    total_pages = max(1, (total + per_page - 1) // per_page) if total else 1
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }
    return items, pagination


def _int_param(request, name: str, default: int) -> int:
    """Extract an integer query parameter, falling back to ``default``.

    Works with both Django HttpRequest (``.GET``) and PyRequest (``.query``).
    """
    try:
        if hasattr(request, "query"):
            val = request.query.get(name, str(default))
        elif hasattr(request, "GET"):
            val = request.GET.get(name, str(default))
        else:
            return default
        return int(val)
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
    """Safely get the current user from a request."""
    if hasattr(request, "user") and request.user and not request.user.is_anonymous:
        return request.user
    from www.auth import authenticate_request

    return authenticate_request(request)


def paginated_response(items, pagination: dict, request, results: list[dict]) -> dict:
    """Return the canonical DRF-style paginated list response."""
    page = int(pagination.get("page", 1) or 1)
    per_page = int(pagination.get("per_page", 20) or 20)
    total = int(pagination.get("total", 0) or 0)
    total_pages = int(pagination.get("total_pages", 1) or 1)

    def page_url(page_number: int) -> str | None:
        if page_number < 1 or page_number > total_pages:
            return None
        try:
            query = request.GET.copy()
            query["page"] = str(page_number)
            if "page_size" in query:
                query["page_size"] = str(per_page)
            else:
                query["per_page"] = str(per_page)
            return request.build_absolute_uri(f"{request.path}?{query.urlencode()}")
        except Exception:
            return None

    return {
        "results": results,
        "count": total,
        "next": page_url(page + 1) if page < total_pages else None,
        "previous": page_url(page - 1) if page > 1 else None,
    }
