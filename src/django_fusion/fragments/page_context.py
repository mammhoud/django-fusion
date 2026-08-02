"""Resolve host-page context for URL-driven fragment requests."""
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
    """Extract a local path from a full URL or return the path unchanged."""
    if not url:
        return None
    if url.startswith(("http://", "https://")):
        parsed = urlparse(url)
        return parsed.path or "/"
    return url or "/"


def resolve_page_context(request, url: str | None = None) -> dict[str, Any]:
    """Resolve a Django/Wagtail page and return its best-effort context.

    When ``url`` is omitted, the originating page is read from HTMX's
    ``HX-Current-URL`` header, then ``page_url`` or ``page_path`` query
    parameters. Resolution failures return an empty context so fragment
    rendering remains independent of the host page.
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

    if Page is not None:
        try:
            if getattr(match, "url_name", None) == "wagtail_serve":
                page = Page.objects.specific().get(url_path=local_path)
                return page.get_context(request) or {}
        except Page.DoesNotExist:
            logger.debug("Wagtail page not found for path: %s", local_path)
            return {}
        except Exception as exc:  # pragma: no cover - Wagtail is optional
            logger.debug("Could not resolve Wagtail page context: %s", exc)

        try:
            page = getattr(match, "kwargs", {}).get("page")
            if isinstance(page, Page):
                return page.get_context(request) or {}
        except Exception as exc:
            logger.debug("Could not extract Wagtail page from kwargs: %s", exc)

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
