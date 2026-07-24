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
import inspect
import json
import logging
from typing import Any, Callable
from urllib.parse import urljoin

from django.http import Http404, JsonResponse
from django.urls import NoReverseMatch, reverse

from www.api.data.helpers import (
    paginate_queryset,
    parse_body,
    get_current_user,
    get_image_url,
    get_user_display_name,
    paginated_response,
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


def fusion_response(
    component: Any,
    request: Any = None,
    *,
    fusion_render_first: bool | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the canonical fragment-pointer payload for a django-fusion component.

    This helper removes the need for bolt views to hand-build dictionaries like::

        {
            "component": "...",
            "fusion_render_first": True,
            "fragment_name": "...",
            "fragment_url": "...",
        }

    ``component`` may be:

    * a ``RoutableComponent``/``FragmentComponent`` **class**,
    * an instance of such a component, or
    * a string fragment name (e.g. ``"components.hero"``).

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

        # Instantiate the component class so we can call instance methods such
        # as ``get_fragment_name()``.  If it cannot be instantiated, fall back
        # to reading class-level attributes.
        instance: Any | None = None
        if is_class:
            try:
                instance = component()
            except Exception:  # noqa: BLE001
                instance = None
        else:
            instance = component

        target = instance if instance is not None else component

        # Determine fusion_render_first.
        #
        # Priority:
        #   1. Explicit ``fusion_render_first`` parameter — highest priority.
        #   2. ``RoutableComponent.get_fusion_render_first()`` classmethod —
        #      respects the COMPONENTS.FUSION_RENDER_FIRST_DEFAULT setting
        #      AND per-component overrides.
        #   3. ``fusion_render_first`` class/instance attribute —
        #      RoutableComponent subclasses define it as ``None`` by
        #      default, which evaluates to ``False``.
        #   4. ``False`` — fallback for arbitrary objects.
        #
        # To enable fragment-first rendering project-wide:
        #   COMPONENTS = { "FUSION_RENDER_FIRST_DEFAULT": True }
        #
        # To enable per-component:
        #   class MyComponent(RoutableComponent):
        #       fusion_render_first = True
        if fusion_render_first is not None:
            resolved_render_first = fusion_render_first
        elif hasattr(target, "get_fusion_render_first"):
            resolved_render_first = target.get_fusion_render_first()
        else:
            resolved_render_first = bool(
                getattr(target, "fusion_render_first", False)
            )

        # Determine fragment_name.  Only call ``get_fragment_name()`` on an
        # instance; calling it on the class itself would raise TypeError.
        resolved_fragment_name = getattr(target, "fragment_name", None)
        if instance is not None:
            get_fragment_name = getattr(instance, "get_fragment_name", None)
            if callable(get_fragment_name):
                try:
                    resolved_fragment_name = get_fragment_name()
                except Exception:  # noqa: BLE001
                    pass

    if not resolved_fragment_name:
        raise ValueError(
            f"Cannot resolve fragment_name for component {component!r}"
        )

    # Lazy import: this module is imported by many API views, and the
    # renderer is only needed when ``fusion_response`` is actually called.
    from django_fusion.fragments.renderer import validate_fragment_name

    try:
        validate_fragment_name(resolved_fragment_name)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(
            f"Invalid fragment_name {resolved_fragment_name!r} for component {component!r}: {exc}"
        ) from exc

    # Build the payload. ``extra`` is merged first so canonical keys cannot be
    # accidentally overwritten, but arbitrary metadata can still be attached.
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
    """Build a fragment URL for *fragment_name*.

    Uses Django URL reversing when available, falling back to the default
    ``/fragments/<name>/`` path.  Returns an absolute URL when *request*
    provides enough context; otherwise returns a relative path.
    """
    # Try the named django-fusion fragment view first.
    try:
        path = reverse("fragments:render", kwargs={"fragment_name": fragment_name})
    except NoReverseMatch:
        path = f"/fragments/{fragment_name}/"

    if request is None:
        return path

    # Django HttpRequest style
    build_abs = getattr(request, "build_absolute_uri", None)
    if callable(build_abs):
        try:
            return build_abs(path)
        except Exception:  # noqa: BLE001
            pass

    # django-bolt PyRequest / generic ASGI/WSGI request style
    request_url = getattr(request, "url", None)
    if request_url:
        try:
            return urljoin(request_url, path)
        except Exception:  # noqa: BLE001
            pass

    # Host header fallback
    headers = getattr(request, "headers", None) or getattr(request, "META", None)
    host = None
    if headers:
        host = headers.get("host") or headers.get("HTTP_HOST")
    if host:
        scheme = getattr(request, "scheme", None) or "http"
        return f"{scheme}://{host}{path}"

    return path


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
    "fusion_response",
    "paginate_queryset",
    "parse_body",
    "get_current_user",
    "get_image_url",
    "get_user_display_name",
    "paginated_response",
    "authenticate_request",
    "extract_bearer_token",
]
