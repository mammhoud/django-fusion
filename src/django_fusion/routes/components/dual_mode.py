"""
Dual-mode rendering for routable components and fragments.

``FusionDualModeMixin`` gives any ``RoutableComponent`` / ``FragmentComponent``
a **render-first** vs **data-mode** contract, mirroring the ``fusion_render_first``
flag already used by ``RoutableComponent``:

* ``fusion_render_first=True``  → the component renders its HTML fragment
  (server-rendered HTML is the source of truth — SEO friendly).
* ``fusion_render_first=False`` → the component returns a codec-encoded JSON
  payload (``FusionCodec``) so a client-side frontend (Astro + Alpine.js,
  Next.js, etc.) can render from data. The payload includes the **Site**
  encapsulation (navigation, apps, branding, active language) so the client
  can build chrome around the content.

Usage::

    from django_fusion.routes.components.dual_mode import FusionDualModeMixin
    from django_fusion.routes.components.fragments import FragmentComponent

    class CourseGridFragment(FusionDualModeMixin, FragmentComponent):
        route_name = "course-grid"
        route_path = "courses/grid/"
        fragment_name = "htmx.course_grid"
        fusion_render_first = True

        def get_fragment_data(self):
            return list(self.get_queryset().values("id", "title", "price"))

Dual mode is also available for full-page ``RoutableComponent`` views — mix it in
and override :meth:`get_fragment_data` (data payload) and optionally
:meth:`get_data_meta` (title / layout / breadcrumbs).
"""

from __future__ import annotations

import logging
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import get_language

from django_fusion.plugins.htmx.core import is_htmx_request
from django_fusion.routes.rendering.renderers import fusion_json_response
from django_fusion.routes.rendering.session import FusionCodec, get_session_render_first

logger = logging.getLogger(__name__)


class FusionDualModeMixin:
    """Route requests between render-first HTML and codec-encoded JSON data.

    The decision is made from :meth:`get_effective_render_first`, which
    prefers the per-request session preference and falls back to the
    component's ``get_fusion_render_first()`` (which itself honours
    ``FUSION_RENDER_FIRST``).

    Subclasses should implement:

    * :meth:`get_fragment_data` — the JSON-serialisable payload used in data
      mode. Defaults to ``{}``.
    * :meth:`get_data_meta` — optional metadata (title, layout, breadcrumbs)
      merged into the data payload. Defaults to a small set derived from the
      component.

    When ``fusion_render_first`` is True the parent rendering pipeline is
    used unchanged (fragment HTML). When False a ``fusion_json_response``
    with ``{encoded, data, site}`` is returned.
    """

    #: Force data mode even when the session/component says render-first.
    force_data_mode: bool = False

    #: Force HTML (render-first) mode even when the session says data mode.
    #: Useful for fragments whose output is inherently HTML (head content,
    #: checkout POST flows, SSE streams).
    force_render_first: bool = False

    def get_effective_render_first(self, request: HttpRequest | None = None) -> bool:
        """Return the effective render-first preference.

        Priority:
        1. ``force_render_first`` — hard override to HTML mode.
        2. ``force_data_mode`` — hard override to data mode.
        3. ``X-Fusion-Render-First`` header — per-request override.
        4. Session preference (``get_session_render_first``) when available.
        5. Component / setting default via ``get_fusion_render_first()``.
        """
        if self.force_render_first:
            return True
        if self.force_data_mode:
            return False

        request = request or getattr(self, "request", None)
        if request is not None:
            # Per-request override lets data-mode clients (Astro, Next.js)
            # opt into a mode for a single request without touching the session.
            header = request.headers.get("X-Fusion-Render-First")
            if header in ("true", "false"):
                return header == "true"

            try:
                # Django's ``request.session`` raises ``ImproperlyConfigured``
                # (not ``AttributeError``) when SessionMiddleware is absent,
                # so gate on the middleware via a nested try.
                if hasattr(request, "session"):
                    return bool(get_session_render_first(request))
            except Exception:
                logger.debug("Session preference unavailable, falling back to default", exc_info=True)

        return bool(self.get_fusion_render_first())  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # Data payload
    # ------------------------------------------------------------------

    def get_fragment_data(self) -> dict[str, Any]:
        """Return the JSON-serialisable payload for data mode.

        Override in subclasses. Defaults to ``{}``.
        """
        return {}

    def get_data_meta(self) -> dict[str, Any]:
        """Return metadata merged into the data-mode payload.

        Includes component identity, render-first flag, fragment name,
        active language, and (when resolvable) the Site encapsulation.
        """
        meta: dict[str, Any] = {
            "component": type(self).__name__,
            "fragment_name": self.get_fragment_name(),  # type: ignore[attr-defined]
            "fusion_render_first": self.get_effective_render_first(),
            "language": get_language(),
        }
        site_ctx = self.get_site_context()
        if site_ctx:
            meta["site"] = site_ctx
        return meta

    def get_site_context(self) -> dict[str, Any] | None:
        """Walk the parent viewset hierarchy to find the enclosing ``Site``.

        Returns ``None`` when no Site is reachable. Otherwise returns a
        serialisable dict with the site title and navigation items, so a
        client-side frontend can render the site chrome (header/footer)
        around data-mode content.
        """
        from django_fusion.routes.core.sites import Application, Site

        site: Site | None = None
        app: Application | None = None
        current = getattr(self, "parent", None)
        while current is not None:
            if isinstance(current, Site) and site is None:
                site = current
            if isinstance(current, Application) and app is None:
                app = current
            current = getattr(current, "parent", None)

        if site is None:
            return None

        navigation: list[dict[str, Any]] = []
        for item in site.menu_items():
            nav_item: dict[str, Any] = {}
            if isinstance(item, Application):
                nav_item = {
                    "type": "application",
                    "title": item.title,
                    "icon": getattr(item, "icon", ""),
                    "app_name": getattr(item, "app_name", None),
                    "active": item is app,
                    "menu_items": [
                        {
                            "title": getattr(menu, "title", None),
                            "icon": getattr(menu, "icon", "view_carousel"),
                            "name": getattr(menu, "name", None),
                        }
                        for menu in item.menu_items()
                        if getattr(menu, "show_in_menu", True)
                    ],
                }
            else:
                nav_item = {
                    "type": "item",
                    "title": getattr(item, "title", None),
                    "icon": getattr(item, "icon", "dashboard"),
                    "name": getattr(item, "name", None),
                }
            navigation.append(nav_item)

        return {
            "title": site.title,
            "navigation": navigation,
            "active_app": app.title if app else None,
        }

    # ------------------------------------------------------------------
    # Rendering dispatch
    # ------------------------------------------------------------------

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Route GET/HEAD requests to data mode when render-first is False.

        Only safe (read-only) methods are intercepted so that POST/PUT/DELETE
        action endpoints (e.g. checkout, blog post creation) always run their
        normal handler even when the client prefers data mode.

        When data mode is active the request is served as JSON without
        running the normal template pipeline. Otherwise the parent
        ``dispatch()`` (fragment or full-page rendering) is used.
        """
        if request.method in ("GET", "HEAD") and not self.get_effective_render_first(request):
            return self.render_data_response(request)
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]

    def render_data_response(self, request: HttpRequest | None = None) -> JsonResponse:
        """Build the codec-encoded JSON payload response.

        Payload shape::

            {
              "status": 200,
              "message": "Success",
              "data": {
                "encoded": "fusion_v1:<base64>",
                "meta": { ... component identity + site navigation ... },
              }
            }

        The client-side ``FusionDecoder`` can decode ``data.encoded`` to the
        raw payload from :meth:`get_fragment_data`.

        When the request came from HTMX the response also carries
        ``HX-Partial: true`` so fragment-aware clients treat it consistently.
        """
        request = request or getattr(self, "request", None)
        payload = self.get_fragment_data()
        meta = self.get_data_meta()

        encoded = FusionCodec.encode(payload)
        response = fusion_json_response(
            data={
                "encoded": encoded,
                "meta": meta,
            },
            status=200,
        )
        # Note: data mode targets ``fetch``/JSON clients (Astro, Next.js).
        # HTMX element swaps expect HTML fragments — when an HTMX request
        # arrives in data mode we still tag it so the client can branch.
        if request is not None and is_htmx_request(request):
            response["HX-Partial"] = "true"
        return response


__all__ = ["FusionDualModeMixin"]
