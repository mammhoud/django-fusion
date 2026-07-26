"""
Fusion bolt decorators — dual-purpose endpoint registration.

The ``@fusion_endpoint`` decorator marks a method as both a django-bolt
route AND a fragment-renderer. Depending on ``fusion_render_first``, the
endpoint returns either server-rendered HTML or a JSON fragment pointer.

Usage::

    from django_fusion.bolt import fusion_endpoint

    class MyComponent(RoutableComponent):
        route_path = "dashboard/"

        @fusion_endpoint
        def get(self, request):
            return self.render(request)
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger("django_fusion.bolt")


def fusion_endpoint(
    func: Callable | None = None,
    *,
    render_first: bool | None = None,
    fragment_name: str | None = None,
):
    """Decorator that registers a bolt route AND enables fragment rendering.

    When ``fusion_render_first`` is ``True`` (from request header or
    session), the wrapped function returns rendered HTML. When ``False``
    or not specified, it returns a fragment pointer.

    Can be used as a plain decorator ``@fusion_endpoint`` or with
    parameters: ``@fusion_endpoint(render_first=False)``.

    Args:
        render_first: Force render-first mode on/off.
        fragment_name: Override the fragment name in the pointer response.
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            # Determine render-first from request
            effective_rf = render_first

            if effective_rf is None:
                # Check header
                hdr = getattr(request, "headers", {}).get(
                    "X-Fusion-Render-First", ""
                )
                if hdr.lower() == "true":
                    effective_rf = True
                elif hdr.lower() == "false":
                    effective_rf = False

            if effective_rf is None:
                # Check session
                session = getattr(request, "session", {})
                effective_rf = session.get("fusion_render_first", False)

            # Call the original function
            result = fn(request, *args, **kwargs)

            if effective_rf:
                # Return rendered HTML (the function already did the rendering)
                return result
            else:
                # Wrap as fragment pointer
                component_name = getattr(fn, "__qualname__", fn.__name__)
                fn_name = fragment_name or f"components.{fn.__name__}"

                return {
                    "status": 200,
                    "message": "Success",
                    "data": {
                        "component": component_name,
                        "fragment_name": fn_name,
                        "fragment_url": f"/fragments/{fn_name}/",
                        "fusion_render_first": False,
                    },
                }

        # Store metadata on the wrapper for auto-discovery
        wrapper._fusion_endpoint = True  # type: ignore[attr-defined]
        wrapper._fusion_render_first = render_first  # type: ignore[attr-defined]
        wrapper._fragment_name = fragment_name  # type: ignore[attr-defined]

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
