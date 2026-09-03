"""
django_fusion.builder.api
=========================

The landing builder data-API road — ``GET /builder/pages/`` and
``GET /builder/pages/<slug>/``.

The abstract ``BuilderPage`` has no table, so the API discovers concrete
subclasses (registered by consuming products) and queries each. Products
include these views under their own protected/public URL prefix.
"""

from __future__ import annotations

import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from django_fusion.builder.models import BuilderPage

logger = logging.getLogger(__name__)


def _concrete_builder_models():
    """Yield concrete BuilderPage subclasses (recursively), de-duplicated."""
    seen: set[str] = set()
    stack = list(BuilderPage.__subclasses__())
    while stack:
        model = stack.pop()
        if model._meta.abstract:
            stack.extend(model.__subclasses__())
            continue
        key = f"{model._meta.app_label}.{model.__name__}"
        if key in seen:
            continue
        seen.add(key)
        yield model
        stack.extend(model.__subclasses__())


def _builder_queryset():
    """Union of live pages across every concrete BuilderPage subclass."""
    from itertools import chain

    querysets = [model.objects.live() for model in _concrete_builder_models()]
    if not querysets:
        return BuilderPage.objects.none()
    return list(chain.from_iterable(querysets))


def _get_builder_page(slug: str):
    """Retrieve a live concrete BuilderPage by slug (defaults to the first)."""
    normalized = slug.strip("/") or ""
    for page in _builder_queryset():
        if normalized and page.slug != normalized:
            continue
        return page
    return None


@require_GET
def builder_page_list(request):
    """GET /builder/pages/ — live builder pages (slug/title/type/theme)."""
    try:
        pages = [
            {
                "slug": page.slug,
                "title": page.title,
                "type": page.__class__.__name__,
                "theme": page.theme,
                "brand": page.brand,
                "dark_mode": page.dark_mode,
            }
            for page in _builder_queryset()
        ]
    except Exception as exc:
        logger.exception("builder_page_list error")
        return JsonResponse({"error": str(exc)}, status=500)
    return JsonResponse({"pages": pages})


@require_GET
def builder_page_data(request, slug):
    """GET /builder/pages/<slug>/ — full resolved page payload."""
    page = _get_builder_page(slug)
    if page is None:
        return JsonResponse({"error": "Page not found"}, status=404)
    try:
        specific = page.specific
        return JsonResponse(specific.builder_payload())
    except Exception as exc:
        logger.exception("builder_page_data error for slug=%s", slug)
        return JsonResponse({"error": str(exc)}, status=500)


__all__ = ["builder_page_data", "builder_page_list"]
