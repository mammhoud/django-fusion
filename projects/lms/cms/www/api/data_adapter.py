"""
Data adapter — bridge data-style function views with Django URL routing.

Provides a ``@bolt_view`` decorator that converts a data-style handler
(returning dict or (dict, status)) into a Django function view suitable for
use with ``django.urls.path()``.

Usage::

    from www.api.data_adapter import bolt_view

    @bolt_view
    def my_endpoint(request):
        return {"status": "success", "data": {...}}
        # or
        return {"status": "error", "message": "..."}, 404
"""

from __future__ import annotations

import functools
import json
import logging
from typing import Any, Callable

from django.http import Http404, JsonResponse

from www.api.data.helpers import (
    paginate_queryset,
    parse_body,
    get_current_user,
    get_image_url,
    get_user_display_name,
)
from www.auth import authenticate_request, extract_bearer_token

logger = logging.getLogger(__name__)


def bolt_view(view_func: Callable) -> Callable:
    """Decorator that adapts a data-style handler for Django URL routing.

    The wrapped function receives ``(request, *args, **kwargs)`` and should
    return either a dict (converted to 200 JsonResponse) or a tuple of
    ``(dict, status_code)``.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            result = view_func(request, *args, **kwargs)
            if isinstance(result, tuple):
                data, status = result
                return JsonResponse(data, status=status)
            return JsonResponse(result)
        except Http404:
            raise  # Let Django handle 404 properly
        except Exception as exc:
            logger.exception("Bolt view error: %s", exc)
            return JsonResponse(
                {"status": "error", "message": "Internal server error"},
                status=500,
            )
    return wrapper


def login_required(view_func: Callable) -> Callable:
    """Bolt-style login_required decorator (returns 401 JSON, not a redirect).

    Checks token auth first, then Django session auth.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            user = authenticate_request(request)
            if user is not None:
                request.user = user
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "Authentication required"},
                status=401,
            )
        return view_func(request, *args, **kwargs)
    return wrapper


# Re-export bolt helpers for convenience
__all__ = [
    "bolt_view",
    "login_required",
    "paginate_queryset",
    "parse_body",
    "get_current_user",
    "get_image_url",
    "get_user_display_name",
    "authenticate_request",
    "extract_bearer_token",
]
