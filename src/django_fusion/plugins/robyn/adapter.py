"""
RobynAdapter — mounts django-fusion viewsets and routes onto a Robyn app.

Bridges the gap between django-fusion's ``Viewset`` / ``Application`` routing
system and Robyn's async route decorators.  Lets POS sidecars replace
hand-written ``_register_crud`` boilerplate with django-fusion model viewsets.

Usage::

    from robyn import Robyn
    from django_fusion.comp.robyn import RobynAdapter
    from myapp.viewsets import ProductViewSet, CategoryViewSet

    app = Robyn(__file__)
    adapter = RobynAdapter(app)

    adapter.register(ProductViewSet)
    adapter.register(CategoryViewSet)

    # Or mount a whole Application:
    from django_fusion.routes.core.sites import Application
    from django_fusion.routes.models.crud import ModelViewset

    class POSApi(Application):
        @viewprop
        def viewsets(self):
            return [ProductViewSet(), CategoryViewSet()]

    adapter.mount(POSApi())
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import logging
from typing import Any

logger = logging.getLogger("django_fusion.robyn")


class RobynAdapter:
    """Registers django-fusion routes on a Robyn app.

    Each django-fusion ``Viewset`` or ``RoutableComponent`` is introspected
    and its routes are registered as Robyn ``@app.get``, ``@app.post``, etc.
    decorators.  Wraps each handler to convert Robyn's ``Request`` into a
    django-fusion-compatible ``RobynRequest`` before calling the view.
    """

    def __init__(self, app: Any) -> None:
        self._app = app
        self._prefix: str = ""
        self._registered: int = 0

    # ── Registration ──────────────────────────────────────────────────

    def set_prefix(self, prefix: str) -> "RobynAdapter":
        """Set a URL prefix for all subsequently registered routes."""
        self._prefix = prefix.rstrip("/")
        return self

    def register(self, viewset_or_component: Any) -> None:
        """Register all routes from a viewset or routable component.

        Accepts any object with a ``routes`` attribute (``Viewset``,
        ``RoutableComponent``, ``FragmentComponent``) or an iterable
        of ``Route`` objects.

        Usage::

            adapter.register(ProductViewSet())
            adapter.register(MyFragmentComponent())
        """
        routes = _get_routes(viewset_or_component)
        if not routes:
            logger.debug("No routes to register for %s", type(viewset_or_component).__name__)
            return

        for route in routes:
            self._register_route(route)

    def mount(self, application_or_site: Any) -> None:
        """Mount all viewsets and components from an Application or Site.

        Usage::

            from django_fusion.routes.core.sites import Application

            class MyApp(Application):
                @viewprop
                def viewsets(self):
                    return [ProductViewSet(), DashboardFragment()]

            RobynAdapter(app).mount(MyApp())
        """
        prefix = getattr(application_or_site, "url_prefix", "") or ""
        old_prefix = self._prefix
        if prefix:
            self._prefix = prefix.rstrip("/")

        # Application.viewsets is typically a @viewprop that returns a list
        if hasattr(application_or_site, "viewsets"):
            viewsets = _maybe_call(application_or_site.viewsets)
            if isinstance(viewsets, (list, tuple)):
                for vs in viewsets:
                    self.register(vs)

        self._prefix = old_prefix
        logger.info(
            "Mounted %s — %d routes registered",
            type(application_or_site).__name__,
            self._registered,
        )

    # ── Internal ──────────────────────────────────────────────────────

    def _register_route(self, route: Any) -> None:
        """Register a single Route on the Robyn app."""
        path = self._build_path(route)
        methods = _get_methods(route)
        handler = _get_handler(route)

        if handler is None:
            return

        wrapped = self._wrap_handler(handler)

        for method in methods:
            decorator = getattr(self._app, method.lower(), None)
            if decorator is None:
                logger.warning("Unsupported HTTP method %s for %s", method, path)
                continue
            decorator(path)(wrapped)

        self._registered += 1
        logger.debug("Registered %s %s → %s", methods, path, _handler_name(handler))

    def _build_path(self, route: Any) -> str:
        """Build the full URL path for a route."""
        route_path = getattr(route, "path", "") or getattr(route, "url_path", "") or ""
        if not route_path:
            route_path = getattr(route, "route_path", "") or ""
        if not route_path:
            name = getattr(route, "route_name", "") or getattr(route, "name", "") or ""
            route_path = name.replace("_", "-")

        prefix = self._prefix
        path = f"/{prefix}/{route_path}" if prefix else f"/{route_path}"
        # Collapse multiple slashes
        while "//" in path:
            path = path.replace("//", "/")
        return path

    def _wrap_handler(self, handler: Any) -> Any:
        """Wrap a django-fusion view handler for Robyn.

        Returns an async callable that:
        1. Reads the Robyn request body (if needed)
        2. Wraps it in ``RobynRequest``
        3. Calls the original django-fusion handler
        4. Converts the result to a Robyn ``Response``
        """
        from .request import RobynRequest

        if inspect.iscoroutinefunction(handler) or _is_async(handler):

            @functools.wraps(handler)
            async def async_wrapper(request, **kwargs):
                try:
                    fusion_req = RobynRequest(request)
                    await fusion_req.read_body()
                    result = await handler(fusion_req, **kwargs)
                    return _to_robyn_response(result)
                except Exception:
                    logger.exception(
                        "Unhandled exception in async handler %s (%s %s)",
                        _handler_name(handler),
                        getattr(request, "method", "?"),
                        getattr(request, "url", getattr(request, "path", "?")),
                    )
                    return _error_500_response()

            return async_wrapper
        else:

            @functools.wraps(handler)
            async def sync_wrapper(request, **kwargs):
                try:
                    fusion_req = RobynRequest(request)
                    await fusion_req.read_body()
                    # Offload sync handler to a thread to avoid blocking
                    # Robyn's async event loop (required for production).
                    # Closure captures kwargs so path parameters reach the
                    # django-fusion handler (empty **kwargs expands to nothing).
                    loop = asyncio.get_running_loop()

                    def _runner():
                        return handler(fusion_req, **kwargs)

                    result = await loop.run_in_executor(None, _runner)
                    return _to_robyn_response(result)
                except Exception:
                    logger.exception(
                        "Unhandled exception in sync handler %s (%s %s)",
                        _handler_name(handler),
                        getattr(request, "method", "?"),
                        getattr(request, "url", getattr(request, "path", "?")),
                    )
                    return _error_500_response()

            return sync_wrapper


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_routes(obj: Any) -> list[Any]:
    """Extract routes from a viewset, component, or route list."""
    if isinstance(obj, (list, tuple)):
        return list(obj)

    # Viewset / RoutableComponent have a .routes attribute
    if hasattr(obj, "routes"):
        routes = _maybe_call(obj.routes)
        if isinstance(routes, (list, tuple)):
            return list(routes)

    # Fallback: try iterating the object itself
    if hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes)):
        try:
            return list(obj)
        except TypeError:
            pass

    return []


def _get_methods(route: Any) -> list[str]:
    """Get HTTP methods for a route (default: GET)."""
    methods = getattr(route, "methods", None)
    if methods is None:
        return ["GET"]
    if isinstance(methods, str):
        return [m.strip().upper() for m in methods.split(",")]
    return [str(m).strip().upper() for m in methods]


def _get_handler(route: Any) -> Any:
    """Get the handler callable for a route."""
    # Route objects may have .view_func, .handler, .view, or .callback
    for attr in ("view_func", "handler", "view", "callback"):
        val = getattr(route, attr, None)
        if val is not None:
            return val
    # If the route itself is callable, use it directly
    if callable(route):
        return route
    return None


def _maybe_call(obj: Any) -> Any:
    """Call ``obj`` if it's a callable that takes no arguments, else return it."""
    if not callable(obj):
        return obj
    try:
        sig = inspect.signature(obj)
        if not sig.parameters:
            return obj()
    except (ValueError, TypeError):
        pass
    return obj


def _handler_name(handler: Any) -> str:
    """Human-readable name for a handler."""
    return getattr(handler, "__name__", str(handler))


def _is_async(obj: Any) -> bool:
    """Check if a callable is async (coroutine function or awaitable)."""
    if inspect.iscoroutinefunction(obj):
        return True
    if hasattr(obj, "__call__") and inspect.iscoroutinefunction(obj.__call__):
        return True
    return False


def _error_500_response() -> Any:
    """Return a Robyn 500 Internal Server Error JSON response."""
    from robyn import jsonify
    return jsonify({"error": "Internal server error"}, status=500)


def _to_robyn_response(result: Any) -> Any:
    """Convert a django-fusion view result to a Robyn Response."""
    from robyn import Response, jsonify

    if result is None:
        return Response(status_code=204, headers={}, description="")

    if isinstance(result, Response):
        return result

    # Django HttpResponse
    if hasattr(result, "status_code") and hasattr(result, "content"):
        headers = dict(result.items()) if hasattr(result, "items") else {}
        return Response(
            status_code=result.status_code,
            headers=headers,
            description=result.content.decode("utf-8", errors="replace")
            if isinstance(result.content, bytes)
            else str(result.content),
        )

    # Dict / list → JSON
    if isinstance(result, (dict, list)):
        return jsonify(result)

    # String → plain text
    return Response(
        status_code=200,
        headers={"content-type": "text/plain; charset=utf-8"},
        description=str(result),
    )


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def register_viewset(app: Any, viewset: Any) -> None:
    """Convenience function — register a single viewset on a Robyn app.

    Equivalent to::

        RobynAdapter(app).register(viewset)
    """
    RobynAdapter(app).register(viewset)
