"""
Function-view decorators for django-fusion rendering.

The class-based roads (``Application.respond``, ``APISViewMixin``,
``FusionPageView``) already expose the dual-mode contract.  ``fusion_view``
brings the same option to **plain function views** — the common case for
small product endpoints — so a single view function can respond as either:

* **Render-first (component road)** — server-rendered HTML from a template,
  with ``data`` in the context (``fusion_render_first=True``), or
* **Data API road** — the codec-encoded JSON payload
  (``fusion_render_first=False`` / JSON client).

The mode is resolved by the canonical :func:`resolve_render_first` chain
(header override → session preference → per-view default → setting), so the
decorator never re-implements mode resolution.

Usage::

    from django_fusion.routes.rendering.decorators import fusion_view

    @fusion_view(template_name="components/products/list.html")
    def product_list(request):
        return {"products": Product.objects.all(), "total": 42}

    # GET /products/?X-Fusion-Render-First=true   → rendered HTML component
    # GET /products/?X-Fusion-Render-First=false  → {status, message, data:{encoded,...}}
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string

from django_fusion.routes.rendering.render_mode import resolve_render_first
from django_fusion.routes.rendering.renderers import fusion_json_response
from django_fusion.routes.rendering.session import FusionCodec

__all__ = ["fusion_view", "dual_mode"]


def fusion_view(
    *,
    template_name: str | None = None,
    fusion_render_first: bool | None = None,
    force_data_mode: bool = False,
    message: str | None = None,
    context_processors: list[Callable] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., HttpResponse]]:
    """Decorate a plain function view with the dual-mode response contract.

    The wrapped view must **return a plain Python object** (dict / list /
    ORM values).  ``fusion_view`` decides what to send:

    * ``True``  (render-first) → ``HttpResponse`` built from
      ``template_name`` with ``{"data": <returned object>, "request": …}``
      merged into the context.  Without a template it falls back to a JSON
      payload marked ``rendered=False`` rather than crashing.
    * ``False`` (data API) → ``fusion_json_response`` shaped
      ``{status, message, data: {encoded, data, view_name}}`` where
      ``encoded`` is ``FusionCodec.encode(...)``.

    Keyword options:

    * ``template_name`` — component template for the render-first road.
    * ``fusion_render_first`` — per-view default (``None`` → the Django
      ``FUSION_RENDER_FIRST`` setting / session / header decide).
    * ``force_data_mode`` — hard override to the data-API road.
    * ``message`` — optional message on JSON responses.
    * ``context_processors`` — extra callables ``(request) -> dict`` merged
      into the render-first context.

    If the wrapped view already returns an ``HttpResponse`` (e.g. a
    redirect), it is passed through untouched.
    """

    def decorator(view_func: Callable[..., Any]) -> Callable[..., HttpResponse]:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            result = view_func(request, *args, **kwargs)
            if isinstance(result, HttpResponse):
                return result

            render_first = resolve_render_first(
                request,
                force_data_mode=force_data_mode,
                default=fusion_render_first,
                setting_default=True,
            )

            if not render_first:
                payload: dict[str, Any] = {
                    "encoded": FusionCodec.encode(result),
                    "data": result,
                    "view_name": view_func.__name__,
                }
                return fusion_json_response(payload, message=message)

            if not template_name:
                payload = {"rendered": False, "reason": "no-template", "data": result}
                return fusion_json_response(
                    payload, message=message or "Component response unavailable"
                )

            base_context: dict[str, Any] = {
                "data": result,
                "request": request,
                "fusion_render_first": True,
            }
            for processor in context_processors or []:
                try:
                    base_context.update(processor(request) or {})
                except Exception:  # noqa: BLE001 - processors must never break a page
                    continue
            html = render_to_string(template_name, base_context, request=request)
            return HttpResponse(html, status=200)

        return wrapper

    return decorator


# Backwards-friendly alias: the plugin name used across the docs.
dual_mode = fusion_view
