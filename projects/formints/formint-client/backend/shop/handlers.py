"""
Shop — django-fusion HTMX fragment handlers (mirrors formint/handlers.py).

Each handler owns its ``FragmentComponent`` and returns the same lean HTMX
fragment contract the Astro shell swaps in, honouring the dual-mode
render-first option via ``X-Fusion-Render-First``:

* ``fusion_render_first=True``  → ``component.render_fragment_response()``
  (django-fusion renderer — fragment + OOB + ``HX-Partial``).
* ``fusion_render_first=False`` → ``render(request, template, context)``
  (plain HTML data-only fragment).

Cart actions (add/update/remove) return the swapped fragment + ``HX-Trigger``
so the drawer and badge stay in sync in a single round-trip.
"""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from django_fusion.plugins.htmx import is_htmx_request

from . import services
from .fusion import get_effective_render_first
from .fusion_components import CartCountFragment, CartDrawerFragment, ProductGridFragment
from .models import Product

__all__ = [
    "ProductGridHandler",
    "CartCountHandler",
    "CartDrawerHandler",
    "CartAddHandler",
    "CartUpdateHandler",
    "CartRemoveHandler",
    "CartNoteHandler",
    "get_handler_response",
]


def _not_htmx(payload: dict[str, Any]) -> JsonResponse:
    return JsonResponse(payload, status=406)


def _fragment_response(request, component) -> HttpResponse:
    """Render a fragment component through the dual-mode contract."""
    if get_effective_render_first(request):
        response = component.render_fragment_response(component.get_fragment_context())
        response["X-FormintC-Response-Mode"] = "django-fusion-fragment"
    else:
        context = component.get_fragment_context()
        response = render(request, component.template_name, context)
        response["X-FormintC-Response-Mode"] = "htmx-data-only"
    response["Cache-Control"] = "no-store"
    return response


class ProductGridHandler:
    """GET /shop/fragments/products/ — product card grid (category filterable)."""

    component_class = ProductGridFragment

    def get(self, request: HttpRequest) -> HttpResponse:
        if not is_htmx_request(request):
            return _not_htmx(
                {
                    "detail": "This endpoint is an HTMX data fragment.",
                    "product": "formintc-purchase",
                }
            )
        component = self.component_class()
        component.setup(request)
        return _fragment_response(request, component)


class CartCountHandler:
    """GET /shop/fragments/cart/count/ — cart badge fragment."""

    component_class = CartCountFragment

    def get(self, request: HttpRequest) -> HttpResponse:
        if not is_htmx_request(request):
            return _not_htmx(
                {
                    "detail": "This endpoint is an HTMX data fragment.",
                    "product": "formintc-purchase",
                }
            )
        component = self.component_class()
        component.setup(request)
        return _fragment_response(request, component)


class CartDrawerHandler:
    """GET /shop/fragments/cart/drawer/ — cart drawer body fragment."""

    component_class = CartDrawerFragment

    def get(self, request: HttpRequest) -> HttpResponse:
        if not is_htmx_request(request):
            return _not_htmx(
                {
                    "detail": "This endpoint is an HTMX data fragment.",
                    "product": "formintc-purchase",
                }
            )
        component = self.component_class()
        component.setup(request)
        return _fragment_response(request, component)


class CartAddHandler:
    """POST /shop/cart/add/ — add a product to the session cart."""

    def post(self, request: HttpRequest) -> HttpResponse:
        if not is_htmx_request(request):
            return _not_htmx({"detail": "HTMX action — use from the Astro shell"})

        product = get_object_or_404(Product, pk=request.POST.get("product_id"))
        quantity = int(request.POST.get("quantity", 1) or 1)
        cart = services.get_or_create_cart(request)
        services.add_item(cart, product, quantity)

        # Swap the count badge; the drawer re-fetches on cartUpdated.
        component = CartCountFragment()
        component.setup(request)
        response = _fragment_response(request, component)
        response["HX-Trigger"] = "cartUpdated"
        return response


class CartUpdateHandler:
    """POST /shop/cart/update/<item_id>/ — set a line quantity."""

    def post(self, request: HttpRequest, item_id: int) -> HttpResponse:
        if not is_htmx_request(request):
            return _not_htmx({"detail": "HTMX action — use from the Astro shell"})

        quantity = int(request.POST.get("quantity", 1) or 0)
        cart = services.get_or_create_cart(request)
        services.set_quantity(cart, item_id, quantity)

        component = CartDrawerFragment()
        component.setup(request)
        response = _fragment_response(request, component)
        response["HX-Trigger"] = "cartUpdated"
        return response


class CartRemoveHandler:
    """POST /shop/cart/remove/<item_id>/ — drop a line from the cart."""

    def post(self, request: HttpRequest, item_id: int) -> HttpResponse:
        if not is_htmx_request(request):
            return _not_htmx({"detail": "HTMX action — use from the Astro shell"})

        cart = services.get_or_create_cart(request)
        services.remove_item(cart, item_id)

        component = CartDrawerFragment()
        component.setup(request)
        response = _fragment_response(request, component)
        response["HX-Trigger"] = "cartUpdated"
        return response


class CartNoteHandler:
    """POST /shop/cart/note/<item_id>/ — set a per-item instruction."""

    def post(self, request: HttpRequest, item_id: int) -> HttpResponse:
        if not is_htmx_request(request):
            return _not_htmx({"detail": "HTMX action — use from the Astro shell"})

        cart = services.get_or_create_cart(request)
        services.set_note(cart, item_id, request.POST.get("note", ""))

        # Re-render the drawer so the saved note is visible; the badge count
        # is unchanged so only the drawer swaps (HX-Trigger keeps parity with
        # the other cart mutations for any other listeners).
        component = CartDrawerFragment()
        component.setup(request)
        response = _fragment_response(request, component)
        response["HX-Trigger"] = "cartUpdated"
        return response


# ── Dispatch helper (kept for function-view compatibility) ─────────────────


def get_handler_response(
    handler_cls, request: HttpRequest, *args, **kwargs
) -> HttpResponse:
    """Instantiate a handler and dispatch GET/POST to it (thin compatibility layer)."""
    handler = handler_cls()
    method = getattr(handler, request.method.lower(), None)
    if method is None:
        method = getattr(handler, "get", None)
    if method is None:
        return HttpResponse(status=405)
    return method(request, *args, **kwargs)
