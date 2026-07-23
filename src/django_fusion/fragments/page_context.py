"""Resolve page-level context from a request so fragments can share it.

The fragment system is designed to render small pieces of a page. When a
fragment is requested from a page (e.g. via HTMX), it is often useful to
inject the same context that the host page would have. This module provides
``resolve_page_context`` which can extract a Wagtail page (or any view-provided
context) from the originating URL.
"""
from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from django.urls import Resolver404, resolve

logger = logging.getLogger("django_fusion.fragments.page_context")

try:
    from wagtail.models import Page
except Exception:  # pragma: no cover - Wagtail may not be installed
    Page = None  # type: ignore[misc,assignment]


def _local_path_from_url(url: str) -> str | None:
    """Extract the local path from a full URL or return the path unchanged."""
    if not url:
        return None
    if url.startswith("http://") or url.startswith("https://"):
        parsed = urlparse(url)
        return parsed.path or "/"
    return url or "/"


def resolve_page_context(request, url: str | None = None) -> dict[str, Any]:
    """Resolve a Django/Wagtail page from *url* and return its context.

    The *url* argument can be a full URL or a local path. If omitted, the
    function falls back to:

    1. ``request.headers.get("HX-Current-URL")``
    2. ``request.GET.get("page_url")``
    3. ``request.GET.get("page_path")``

    For Wagtail pages, ``page.get_context(request)`` is called and the
    returned dict is used. For regular Django views, the resolved view is
    invoked with a cloned request at the target path and its context is
    returned when possible.

    Any error during resolution is swallowed and an empty dict is returned
    so that fragment rendering is never blocked by a failed page lookup.
    Errors are logged for debugging.
    """
    if url is None:
        url = (
            request.headers.get("HX-Current-URL")
            or request.GET.get("page_url")
            or request.GET.get("page_path")
            or ""
        )

    local_path = _local_path_from_url(url)
    if not local_path:
        return {}

    try:
        match = resolve(local_path)
    except Resolver404:
        logger.debug("Could not resolve page path: %s", local_path)
        return {}

    # Try Wagtail page resolution first.
    if Page is not None:
        try:
            if hasattr(match, "url_name") and match.url_name == "wagtail_serve":
                page = Page.objects.specific().get(url_path=local_path)
                if page:
                    return page.get_context(request) or {}
        except Page.DoesNotExist:
            logger.debug("Wagtail page not found for path: %s", local_path)
            return {}
        except Exception as exc:  # pragma: no cover - Wagtail may not be installed
            logger.debug("Could not resolve Wagtail page context: %s", exc)

        # Fallback: try to find a Page in the view's kwargs/context.
        try:
            page = getattr(match, "kwargs", {}).get("page")
            if isinstance(page, Page):
                return page.get_context(request) or {}
        except Exception as exc:
            logger.debug("Could not extract Wagtail page from kwargs: %s", exc)

    # Generic Django view: attempt to call the view and extract context.
    # This is best-effort; many CBVs need extra setup and will simply raise.
    try:
        view = match.func
        if hasattr(view, "view_class"):
            instance = view.view_class()
            instance.request = request
            instance.args = ()
            instance.kwargs = match.kwargs
            if hasattr(instance, "get_context_data"):
                return instance.get_context_data() or {}
    except Exception as exc:
        logger.debug("Could not extract Django view context: %s", exc)

    return {}
