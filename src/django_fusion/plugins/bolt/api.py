"""
FusionBoltAPI — BoltAPI subclass with django-fusion component integration.

Auto-registers ``RoutableComponent`` and ``FragmentComponent`` subclasses as
django-bolt endpoints, exposing fragment data, health checks, and rendering
preferences through the high-performance Rust-backed bolt server.

Usage::

    from django_fusion.plugins.bolt import FusionBoltAPI

    fusion_bolt = FusionBoltAPI(prefix="/api/v2", namespace="fusion")

    # Auto-register all fusion components
    fusion_bolt.autodiscover()

    # Or register individually
    fusion_bolt.register_component(HomePageComponent)

    # Mount in Django URLs
    urlpatterns = [path("api/v2/", fusion_bolt.urls)]
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from django.conf import settings as django_settings
from django.http import HttpRequest

from django_bolt import BoltAPI
from django_bolt.auth import AllowAny

from django_fusion.plugins.bolt.mixins import FUSION_BOLT_AWARE_ATTR
from django_fusion.routes.rendering.session import FusionSessionChecker
from django_fusion.routes.rendering.renderers import fusion_json_response

logger = logging.getLogger("django_fusion.bolt")


class FusionBoltAPI(BoltAPI):
    """BoltAPI subclass that integrates with django-fusion components.

    Features:
    - Auto-discovers ``RoutableComponent`` subclasses and registers bolt endpoints
    - Exposes ``/fusion/health``, ``/fusion/layouts``, ``/fusion/branding``,
      ``/fusion/assets/manifest``, ``/fusion/assets/top``, ``/fusion/assets/bottom``
    - Respects ``fusion_render_first`` per-component setting
    - Generates OpenAPI schemas from component metadata

    Settings (from ``django.conf.settings.FUSION_BOLT``)::

        FUSION_BOLT = {
            "enabled": True,
            "prefix": "/api",
            "openapi_title": "Fusion API",
            "component_auto_register": True,
        }
    """

    def __init__(
        self,
        *args,
        component_auto_register: bool | None = None,
        **kwargs,
    ):
        # Read prefixed settings from FUSION_BOLT config dict
        bolt_config = getattr(django_settings, "FUSION_BOLT", {})
        kwargs.setdefault("prefix", bolt_config.get("prefix", "/api"))

        super().__init__(*args, **kwargs)

        self._auto_register = (
            component_auto_register
            if component_auto_register is not None
            else bolt_config.get("component_auto_register", True)
        )
        self._registered_components: dict[str, type] = {}
        self._checker = FusionSessionChecker()

        # Register built-in fusion endpoints
        self._register_fusion_endpoints()

    # ------------------------------------------------------------------
    # Built-in fusion endpoints
    # ------------------------------------------------------------------

    def _register_fusion_endpoints(self) -> None:
        """Register standard fusion health, layout, branding, and assets endpoints."""

        @self.get("/fusion/health", guards=[AllowAny()], auth=[])
        def fusion_health(request) -> dict:
            """GET /fusion/health — rendering preference check."""
            was_cached = "fusion_render_first" in getattr(request, "session", {})
            preference = self._checker.get_preference(request)
            ua = (
                getattr(request, "META", {}).get("HTTP_USER_AGENT") or ""
            ).lower()[:60]
            return {
                "status": 200,
                "message": "Success",
                "data": {
                    "fusion_render_first": preference,
                    "reason": f"user_agent: {ua}",
                    "session_cached": was_cached,
                },
            }

        @self.get("/fusion/layouts", guards=[AllowAny()], auth=[])
        def fusion_layouts(request) -> dict:
            """GET /fusion/layouts — available layout options."""
            from django_fusion.config.conf import get_settings

            comp_settings = get_settings()
            return {
                "status": 200,
                "message": "Success",
                "data": {
                    "available": comp_settings.LAYOUTS,
                    "default": comp_settings.DEFAULT_LAYOUT,
                },
            }

        @self.get("/fusion/branding", guards=[AllowAny()], auth=[])
        def fusion_branding_endpoint(request) -> dict:
            """GET /fusion/branding — site branding data."""
            import os

            return {
                "site_name": os.environ.get("FUSION_SITE_NAME", "Fusion"),
                "company_name": os.environ.get(
                    "FUSION_COMPANY_NAME", "Fusion Inc."
                ),
                "creator_name": os.environ.get(
                    "FUSION_CREATOR_NAME", "Fusion Team"
                ),
                "primary_color": os.environ.get(
                    "FUSION_PRIMARY_COLOR", "#00a1b3"
                ),
                "secondary_color": os.environ.get(
                    "FUSION_SECONDARY_COLOR", "#008080"
                ),
            }

        # FUSION_ASSETS endpoints — delegate to shared registrar
        register_fusion_assets_bolt(self)

    # ------------------------------------------------------------------
    # Component registration
    # ------------------------------------------------------------------

    def register_component(self, component_cls: type) -> str | None:
        """Auto-generate bolt endpoints for a ``RoutableComponent``.

        Reads ``route_path``, ``route_name``, ``fragment_name``, and
        ``get_fusion_render_first()`` from the component class and
        registers a GET endpoint that returns either JSON data or a
        fragment pointer depending on the client's preference.

        Returns the registered route path, or ``None`` if the component
        has no ``route_path``.
        """
        route_path = getattr(component_cls, "route_path", None)
        if not route_path:
            logger.debug("Skipping component %r: no route_path", component_cls.__name__)
            return None

        # Normalize route path
        path = route_path.strip("/")
        route_path_final = f"/{path}"

        route_name = getattr(component_cls, "route_name", None)
        fragment_name = getattr(component_cls, "fragment_name", None)
        if not fragment_name and route_name:
            fragment_name = f"components.{route_name}"

        # Determine render-first preference
        if hasattr(component_cls, "get_fusion_render_first"):
            render_first_default = component_cls.get_fusion_render_first()
        else:
            render_first_default = False

        comp_cls = component_cls  # capture for closure
        # ---- Determine if the component is bolt-aware (FusionBoltDualModeMixin) ----
        is_bolt_aware = getattr(component_cls, FUSION_BOLT_AWARE_ATTR, False)

        @self.get(
            route_path_final,
            guards=[AllowAny()],
            auth=[],
        )
        def component_endpoint(
            request, *args, _comp=comp_cls, _rf=render_first_default,
            _bolt_aware=is_bolt_aware, **kwargs
        ):
            """Auto-generated endpoint for a fusion component.

            When the component uses ``FusionBoltDualModeMixin`` (``_bolt_aware``),
            data mode serves the full ``get_fragment_data()`` payload (codec-encoded)
            instead of a bare fragment pointer.  Render-first mode still delegates
            to the component's Django view.
            """

            # Determine render mode from request
            render_first = _rf
            if hasattr(request, "headers"):
                hdr = request.headers.get("X-Fusion-Render-First", "")
                if hdr.lower() == "true":
                    render_first = True
                elif hdr.lower() == "false":
                    render_first = False

            # Build component metadata
            title = getattr(_comp, "title", None) or getattr(
                _comp, "page_title", None
            ) or _comp.__name__

            fn = fragment_name or f"components.{_comp.__name__.lower()}"

            pointer = {
                "component": _comp.__name__,
                "fragment_name": fn,
                "fragment_url": f"/fragments/{fn}/",
                "fusion_render_first": render_first,
                "title": title,
                "route_path": route_path,
                "route_name": route_name,
            }

            if render_first:
                # Dispatch to the component's Django view (runs the full
                # template pipeline — fragment HTML or full page).
                try:
                    return _comp.as_view()(request, *args, **kwargs)
                except Exception as exc:
                    logger.exception("Render-first failed for %s", _comp.__name__)
                    return {
                        "status": 500,
                        "message": f"Fragment rendering failed: {exc}",
                        "data": pointer,
                    }

            # ---- Data mode ----
            if _bolt_aware:
                # Instantiate the component and call get_bolt_data_payload()
                # to get the full codec-encoded payload (same shape as
                # FusionDualModeMixin.render_data_response()).
                try:
                    instance = _comp()
                    instance.request = request
                    payload = instance.get_bolt_data_payload(request)
                    return {"status": 200, "message": "Success", "data": payload}
                except Exception as exc:
                    logger.exception("Bolt data mode failed for %s", _comp.__name__)
                    return {
                        "status": 500,
                        "message": f"Data mode failed: {exc}",
                        "data": pointer,
                    }

            # Fallback: non-bolt-aware component → return fragment pointer
            return {"status": 200, "message": "Success", "data": pointer}

        self._registered_components[route_path_final] = component_cls
        logger.info(
            "Registered fusion component %r at %s", component_cls.__name__, route_path_final
        )
        return route_path_final

    # ------------------------------------------------------------------
    # Auto-discovery
    # ------------------------------------------------------------------

    def autodiscover(self) -> int:
        """Auto-discover and register all ``RoutableComponent`` subclasses.

        Scans ``django_fusion.routes.components.routable`` for registered
        components and calls ``register_component()`` for each.

        Returns the number of components registered.
        """
        if not self._auto_register:
            logger.debug("Auto-register is disabled")
            return 0

        # Ensure Django apps are fully loaded before scanning
        from django.apps import apps

        if not apps.ready:
            logger.debug("Django apps not ready; deferring autodiscovery")
            return 0

        count = 0
        try:
            from django_fusion.routes.components.routable import RoutableComponent

            # Find all subclasses of RoutableComponent
            for subclass in _find_routable_components(RoutableComponent):
                if self.register_component(subclass):
                    count += 1
        except Exception as exc:
            logger.warning("Auto-discovery failed: %s", exc)

        logger.info("Auto-discovered %d fusion components", count)
        return count


# ------------------------------------------------------------------
# Standalone FUSION_ASSETS registrar
# ------------------------------------------------------------------


def register_fusion_assets_bolt(api: BoltAPI) -> None:
    """Register FUSION_ASSETS endpoints (*manifest*, *top*, *bottom*) on a
    ``BoltAPI`` instance.

    These endpoints return the CSS, font, and JS asset manifest configured
    via the ``FUSION_ASSETS`` Django setting.  They are consumed by the
    Next.js ``<FusionAssets />`` component.

    Call this after constructing a ``BoltAPI`` instance to ensure the
    three endpoints appear in the generated OpenAPI schema::

        from django_bolt import BoltAPI
        from django_fusion.plugins.bolt import register_fusion_assets_bolt

        api = BoltAPI(prefix="/api")
        register_fusion_assets_bolt(api)

    Registered endpoints:

    * ``GET /fusion/assets/manifest`` — full top + bottom manifest
    * ``GET /fusion/assets/top`` — CSS, fonts, preconnect hints
    * ``GET /fusion/assets/bottom`` — JS scripts for ``</body>``
    """

    @api.get("/fusion/assets/manifest", guards=[AllowAny()], auth=[])
    def fusion_assets_manifest(request) -> dict:
        """GET /fusion/assets/manifest — top/bottom asset manifest."""
        from django_fusion.core.assets.views import _get_assets_config

        config = _get_assets_config()
        return {
            "status": 200,
            "message": "Success",
            "data": {
                "top": config["top"],
                "bottom": config["bottom"],
            },
        }

    @api.get("/fusion/assets/top", guards=[AllowAny()], auth=[])
    def fusion_assets_top(request) -> dict:
        """GET /fusion/assets/top — CSS, fonts, preconnect hints."""
        from django_fusion.core.assets.views import _get_assets_config

        config = _get_assets_config()
        return {
            "status": 200,
            "message": "Success",
            "data": config["top"],
        }

    @api.get("/fusion/assets/bottom", guards=[AllowAny()], auth=[])
    def fusion_assets_bottom(request) -> dict:
        """GET /fusion/assets/bottom — JS scripts for </body>."""
        from django_fusion.core.assets.views import _get_assets_config

        config = _get_assets_config()
        return {
            "status": 200,
            "message": "Success",
            "data": config["bottom"],
        }


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _find_routable_components(base_cls: type) -> list[type]:
    """Recursively find all non-abstract subclasses of *base_cls*."""

    def _is_concrete(cls: type) -> bool:
        return not inspect.isabstract(cls) and cls is not base_cls

    found: list[type] = []
    for sub in base_cls.__subclasses__():
        if _is_concrete(sub):
            found.append(sub)
        found.extend(_find_routable_components(sub))
    return found
