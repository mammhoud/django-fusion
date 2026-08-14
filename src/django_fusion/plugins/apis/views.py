"""
Application-based API views for the django-fusion ``apis`` plugin.

Provides the **dual-mode response action** the ``Application`` class can
use for any view:

* ``fusion_render_first=True``  → the view renders a server-side component
  (template) — HTML is the source of truth.
* ``fusion_render_first=False`` → the view returns a codec-encoded JSON
  payload (``FusionCodec.encode``) — the client renders from data.

The mode is resolved by :meth:`APISViewMixin.get_effective_render_first`
with this priority:

1. ``X-Fusion-Render-First: true|false`` request header — per-request override.
2. ``render_first_mapping`` — per-view-name mapping on the Application
   (e.g. ``{"products/export/": False}``).
3. ``fusion_render_first`` — the Application's default option (``None`` →
   fall through to settings).
4. ``settings.FUSION_RENDER_FIRST`` — global default (legacy
   ``FUSION_RENDER_FIRST_DEFAULT`` / ``COMPONENTS_FUSION_RENDER_FIRST_DEFAULT``
   names still accepted).
"""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string

from django_fusion.routes.rendering.render_mode import (
    header_render_first,
    resolve_render_first,
)
from django_fusion.routes.rendering.renderers import fusion_json_response
from django_fusion.routes.rendering.session import FusionCodec

__all__ = ["APISViewMixin", "APIApplication"]


class APISViewMixin:
    """Dual-mode (component vs codec JSON) response contract for views.

    Mix into any view class (typically an ``Application`` subclass) to gain:

    * ``fusion_render_first`` — the default option for this view/application.
    * ``render_first_mapping`` — per-view-name overrides.
    * :meth:`get_effective_render_first` — resolve the mode for a request.
    * :meth:`respond` — return a component response or a codec JSON response.
    """

    #: Default render mode option. ``None`` falls through to the global
    #: ``FUSION_RENDER_FIRST`` setting.
    fusion_render_first: bool | None = None

    #: Per-view-name overrides: ``{"<view_name>": bool}``. A ``True`` entry
    #: forces render-first for that view; ``False`` forces data mode.
    render_first_mapping: dict[str, bool] = {}

    #: Optional template used when rendering the component in render-first mode.
    template_name: str | None = None

    #: Optional schema class attached to the view (used by /schema endpoints).
    schema_class: Any = None

    def get_fusion_render_first(self) -> bool | None:
        """Return this view's configured default option (or ``None``)."""
        return self.fusion_render_first

    def get_render_first_mapping(self) -> dict[str, bool]:
        """Return the per-view mapping for this view."""
        return dict(self.render_first_mapping)

    def get_effective_render_first(
        self,
        request: HttpRequest | None = None,
        *,
        view_name: str | None = None,
    ) -> bool:
        """Resolve the effective render-first mode for *request*.

        Priority: header → per-view mapping → the canonical
        ``resolve_render_first`` chain (explicit session preference → view
        default → settings).  The API plugin's settings fallback defaults to
        render-first (True) when no setting name is configured.
        """
        # 1. Per-request header override.
        header = header_render_first(request)
        if header is not None:
            return header

        # 2. Per-view mapping.
        if view_name is not None:
            mapping = self.get_render_first_mapping()
            if view_name in mapping:
                return bool(mapping[view_name])

        # 3+. Canonical chain (session preference → view default → setting).
        return resolve_render_first(
            request,
            default=self.get_fusion_render_first(),
            setting_default=True,
        )

    # ------------------------------------------------------------------
    # Response action
    # ------------------------------------------------------------------

    def respond(
        self,
        request: HttpRequest,
        data: Any,
        *,
        view_name: str | None = None,
        template_name: str | None = None,
        context: dict[str, Any] | None = None,
        status: int = 200,
        message: str | None = None,
    ) -> HttpResponse:
        """Return a component response (render-first) or codec JSON response.

        * Render-first → ``TemplateResponse``-style HTML built from
          ``template_name`` (or ``self.template_name``) with ``data`` merged
          into *context*.
        * Data mode → ``fusion_json_response`` shaped ``{status, message,
          data: {encoded, data, schema, view_name}}`` where ``encoded`` is
          ``FusionCodec.encode(data)``.

        Use *view_name* to opt into a ``render_first_mapping`` override for
        this specific call.
        """
        render_first = self.get_effective_render_first(request, view_name=view_name)

        if render_first:
            return self._component_response(request, data, template_name=template_name, context=context, status=status)
        return self._codec_response(data, view_name=view_name, status=status, message=message)

    def _component_response(
        self,
        request: HttpRequest,
        data: Any,
        *,
        template_name: str | None = None,
        context: dict[str, Any] | None = None,
        status: int = 200,
    ) -> HttpResponse:
        """Render *data* through a Django template (component response)."""
        tmpl = template_name or self.template_name
        if not tmpl:
            # Without a template there is no component to render — fall back
            # to a JSON payload carrying the data (rendered=True marker).
            payload = {"rendered": False, "reason": "no-template", "data": data}
            return fusion_json_response(payload, status=status, message="Component response unavailable")

        base_context = {
            "data": data,
            "view": self,
            "request": request,
            "fusion_render_first": True,
        }
        if context:
            base_context.update(context)
        html = render_to_string(tmpl, base_context, request=request)
        return HttpResponse(html, status=status)

    def _codec_response(
        self,
        data: Any,
        *,
        view_name: str | None = None,
        status: int = 200,
        message: str | None = None,
    ) -> JsonResponse:
        """Return the codec-encoded JSON API payload (data mode)."""
        payload = {
            "encoded": FusionCodec.encode(data),
            "data": data,
            "view_name": view_name,
        }
        if self.schema_class is not None:
            payload["schema"] = getattr(self.schema_class, "__name__", "Schema")
        return fusion_json_response(payload, status=status, message=message)

    # ------------------------------------------------------------------
    # Schema helper
    # ------------------------------------------------------------------

    def schema_payload(self) -> dict[str, Any]:
        """Return a JSON-serialisable schema descriptor for this view."""
        return {
            "view_name": getattr(self, "name", self.__class__.__name__),
            "title": getattr(self, "title", ""),
            "schema_class": getattr(self.schema_class, "__name__", None),
            "render_first_mapping": self.get_render_first_mapping(),
            "fusion_render_first": self.get_fusion_render_first(),
        }


class APIApplication(APISViewMixin):
    """An ``Application``-compatible base with the dual-mode respond contract.

    Subclass it in your site the same way you subclass ``Application``::

        class ProductsAPI(APIApplication):
            title = "Products"
            fusion_render_first = True
            template_name = "components/products/list.html"

    The mixin only *adds* the render-first options and ``respond()`` — all
    ``Application``/``Viewset`` routing behaviour is inherited unchanged.
    """

    pass
