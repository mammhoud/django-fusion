"""
CTC Research REST API — bolt-pattern adapter helpers.

Provides a ``@bolt_view`` decorator that converts a data-style handler
(returning (data_dict, status_code)) into a full Django ``HttpResponse``,
and a ``fusion_response`` helper that produces fragment-pointer payloads
compatible with the django-fusion frontend components.

Usage::

    from apps.core.api.data_adapter import bolt_view, fusion_response


    @bolt_view
    def page_detail(request, slug):
        page = STATIC_PAGES.get(slug)
        if page is None:
            return {"status": "error", "message": "Not found"}, 404
        return page
"""

from __future__ import annotations

import inspect
import json
import logging
from typing import Any, Callable
from urllib.parse import urljoin

from django.http import Http404, JsonResponse
from django.urls import NoReverseMatch, reverse

logger = logging.getLogger(__name__)


def bolt_view(view_func: Callable) -> Callable:
    """Decorator that converts a data-returning view into a Django ``HttpResponse``.

    The wrapped function should return one of:
        * ``(data_dict, status_code)`` tuple
        * ``data_dict`` alone (implies 200 OK)
        * an ``HttpResponse`` (passed through unchanged)

    Example::

        @bolt_view
        def my_view(request, **kwargs):
            if error:
                return {"status": "error", "message": "Not found"}, 404
            return {"key": "value"}  # → 200 OK
    """

    def wrapper(request, *args, **kwargs):
        result = view_func(request, *args, **kwargs)

        if isinstance(result, JsonResponse):
            return result

        if isinstance(result, tuple) and len(result) == 2:
            data, status = result
            return JsonResponse(data, status=status)

        return JsonResponse(result, status=200)

    return wrapper


def fusion_response(
    component: Any,
    request: Any = None,
    *,
    fusion_render_first: bool | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the canonical fragment-pointer payload for a django-fusion component.

    ``component`` may be:

    * a ``RoutableComponent``/``FragmentComponent`` **class**,
    * an instance of such a component, or
    * a string fragment name (e.g. ``"pages.home"``).

    ``request`` is optional. When provided, the returned ``fragment_url`` will be
    an absolute URL if the request object supports ``build_absolute_uri`` or
    exposes the Host header.

    ``fusion_render_first`` can be used to override the component's own flag.
    ``extra`` is merged into the returned payload.
    """
    # Resolve the component name and fragment identifier.
    if isinstance(component, str):
        component_name = component
        resolved_fragment_name = component
        resolved_render_first = fusion_render_first if fusion_render_first is not None else False
    else:
        is_class = inspect.isclass(component)
        component_name = component.__name__ if is_class else type(component).__name__

        instance: Any | None = None
        if is_class:
            try:
                instance = component()
            except Exception:
                instance = None
        else:
            instance = component

        target = instance if instance is not None else component

        if fusion_render_first is not None:
            resolved_render_first = fusion_render_first
        elif hasattr(target, "get_fusion_render_first"):
            resolved_render_first = target.get_fusion_render_first()
        else:
            resolved_render_first = bool(
                getattr(target, "fusion_render_first", False)
            )

        resolved_fragment_name = getattr(target, "fragment_name", None)
        if instance is not None:
            get_fragment_name = getattr(instance, "get_fragment_name", None)
            if callable(get_fragment_name):
                try:
                    resolved_fragment_name = get_fragment_name()
                except Exception:
                    pass

    if not resolved_fragment_name:
        raise ValueError(
            f"Cannot resolve fragment_name for component {component!r}"
        )

    from django_fusion.fragments.renderer import validate_fragment_name

    try:
        validate_fragment_name(resolved_fragment_name)
    except Exception as exc:
        raise ValueError(
            f"Invalid fragment_name {resolved_fragment_name!r} for component {component!r}: {exc}"
        ) from exc

    payload: dict[str, Any] = {}
    if extra:
        payload.update(extra)

    payload.update(
        {
            "component": component_name,
            "fusion_render_first": resolved_render_first,
            "fragment_name": resolved_fragment_name,
            "fragment_url": _build_fragment_url(resolved_fragment_name, request),
        }
    )

    return payload


def _build_fragment_url(fragment_name: str, request: Any | None = None) -> str:
    """Build a fragment URL for *fragment_name*."""
    try:
        path = reverse("fragments:render", kwargs={"fragment_name": fragment_name})
    except NoReverseMatch:
        path = f"/fragments/{fragment_name}/"

    if request is None:
        return path

    build_abs = getattr(request, "build_absolute_uri", None)
    if callable(build_abs):
        try:
            return build_abs(path)
        except Exception:
            pass

    request_url = getattr(request, "url", None)
    if request_url:
        try:
            return urljoin(request_url, path)
        except Exception:
            pass

    headers = getattr(request, "headers", None) or getattr(request, "META", None)
    host = None
    if headers:
        host = headers.get("host") or headers.get("HTTP_HOST")
    if host:
        scheme = getattr(request, "scheme", None) or "http"
        return f"{scheme}://{host}{path}"

    return path


__all__ = [
    "bolt_view",
    "fusion_response",
]
