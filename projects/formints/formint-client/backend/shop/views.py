"""
Shop views — django-fusion pipeline for the FormintC purchase app.

Split mirrors formint (``formint/handlers.py`` + ``formint/fusion.py``) and
landing-fusion (``apps/handlers/views.py``):

* Catalog + auth JSON APIs stay plain data endpoints (Astro data source).
* HTMX fragments delegate to the ``shop.handlers`` dual-mode handlers.
* Full pages (checkout / confirmation / my orders) are ``PageHandler``
  subclasses — the unified fragment/layout pipeline with ``require_auth``.
* ``/fusion/*`` exposes the render-mode / navigation / assets / session-mode
  contract (see ``shop.fusion``).
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from django_fusion.routes.pages.handler import PageHandler

from . import services
from .fusion import (
    assets_api,
    branding_api,
    navigation_api,
    render_mode_api,
    session_mode_clear_api,
    session_mode_get_api,
    session_mode_set_api,
)
from .handlers import (
    CartAddHandler,
    CartCountHandler,
    CartDrawerHandler,
    CartRemoveHandler,
    CartUpdateHandler,
    ProductGridHandler,
    get_handler_response,
)
from .models import Category, Order, Product

__all__ = [
    "catalog_api",
    "auth_status_api",
    "products_fragment",
    "cart_count_fragment",
    "cart_drawer_fragment",
    "cart_add",
    "cart_update",
    "cart_remove",
    "checkout_page",
    "place_order",
    "order_confirmation",
    "my_orders",
    "render_mode",
    "navigation",
    "branding",
    "assets",
    "session_mode",
]


# ── Catalog JSON (consumed by the Astro build/dev server) ──────────────────


@require_GET
def catalog_api(request: HttpRequest) -> JsonResponse:
    """Categories + available products, JSON — the storefront's data source."""
    categories = Category.objects.filter(is_active=True)
    data = {
        "shop": {
            "name": settings.SHOP_NAME,
            "tagline": settings.SHOP_TAGLINE,
            "order_types": [
                {"value": v, "label": label} for v, label in settings.SHOP_ORDER_TYPES
            ],
        },
        "categories": [
            {
                "id": c.pk,
                "name": c.name,
                "slug": c.slug,
                "glyph": c.glyph,
                "description": c.description,
            }
            for c in categories
        ],
        "products": [
            {
                "id": p.pk,
                "name": p.name,
                "slug": p.slug,
                "description": p.description,
                "price": str(p.price),
                "compare_at_price": str(p.compare_at_price) if p.compare_at_price else None,
                "image_url": p.image_url,
                "unit": p.unit,
                "category": p.category.slug,
                "tags": p.tags,
                "is_featured": p.is_featured,
            }
            for p in Product.objects.filter(
                is_available=True, category__is_active=True
            ).select_related("category")
        ],
    }
    return JsonResponse(data)


@require_GET
def auth_status_api(request: HttpRequest) -> JsonResponse:
    """Session auth status — consumed by the Astro header's Alpine state."""
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False, "user": None})
    user = request.user
    return JsonResponse(
        {
            "authenticated": True,
            "user": {
                "email": user.email,
                "display": getattr(user, "first_name", "") or user.email,
                "is_staff": bool(getattr(user, "is_staff", False)),
            },
        }
    )


# ── HTMX fragments (django-fusion handlers) ────────────────────────────────


@require_GET
def products_fragment(request: HttpRequest):
    """HTMX fragment — product card grid (category filterable)."""
    return get_handler_response(ProductGridHandler, request)


@require_GET
def cart_count_fragment(request: HttpRequest):
    """HTMX fragment — cart badge."""
    return get_handler_response(CartCountHandler, request)


@require_GET
def cart_drawer_fragment(request: HttpRequest):
    """HTMX fragment — cart drawer body."""
    return get_handler_response(CartDrawerHandler, request)


@require_POST
def cart_add(request: HttpRequest):
    return get_handler_response(CartAddHandler, request)


@require_POST
def cart_update(request: HttpRequest, item_id: int):
    return get_handler_response(CartUpdateHandler, request, item_id)


@require_POST
def cart_remove(request: HttpRequest, item_id: int):
    return get_handler_response(CartRemoveHandler, request, item_id)


# ── Full pages (PageHandler — unified fragment/layout pipeline) ─────────────


class CheckoutPageView(PageHandler):
    """Server-rendered checkout with a live HTMX cart summary."""

    template_name = "shop/checkout.html"
    page_title = "Checkout"

    def get_context_data(self, request=None, **kwargs):
        context = super().get_context_data(request=request, **kwargs)
        cart = services.get_or_create_cart(request)
        context.update(
            {
                "cart_payload": services.cart_payload(cart),
                "shop": {
                    "name": settings.SHOP_NAME,
                    "order_types": settings.SHOP_ORDER_TYPES,
                },
            }
        )
        return context

    def get(self, request, *args, **kwargs):
        cart = services.get_or_create_cart(request)
        if not services.cart_payload(cart)["items"]:
            # The storefront home is served by the Astro frontend at "/".
            return redirect("/")
        return super().get(request, *args, **kwargs)


checkout_page = CheckoutPageView.as_view()


class OrderConfirmationPageView(PageHandler):
    """Order placed — reference + line items summary."""

    template_name = "shop/order_confirmation.html"
    page_title = "Order confirmation"

    def get_context_data(self, request=None, **kwargs):
        context = super().get_context_data(request=request, **kwargs)
        context["order"] = get_object_or_404(
            Order, reference=kwargs.get("reference", "").upper()
        )
        return context


order_confirmation = OrderConfirmationPageView.as_view()


class MyOrdersPageView(PageHandler):
    """Order history for the signed-in customer."""

    template_name = "shop/my_orders.html"
    page_title = "My orders"
    require_auth = True
    login_url = reverse_lazy("account_login")

    def get_context_data(self, request=None, **kwargs):
        context = super().get_context_data(request=request, **kwargs)
        context["orders"] = Order.objects.filter(user=request.user)
        return context


my_orders = MyOrdersPageView.as_view()


# ── Order placement ─────────────────────────────────────────────────────────


@require_POST
def place_order(request: HttpRequest):
    """Convert the session cart into an Order."""
    cart = services.get_or_create_cart(request)
    payload = services.cart_payload(cart)
    if not payload["items"]:
        # The storefront home is served by the Astro frontend at "/".
        return redirect("/")

    order_type = request.POST.get("order_type", Order.OrderType.TAKEAWAY)
    if order_type not in Order.OrderType.values:
        order_type = Order.OrderType.TAKEAWAY

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        customer_name=request.POST.get("customer_name", "").strip() or "Guest",
        customer_email=request.POST.get("customer_email", "").strip(),
        customer_phone=request.POST.get("customer_phone", "").strip(),
        order_type=order_type,
        notes=request.POST.get("notes", "").strip(),
        subtotal=Decimal(str(payload["subtotal"])),
        tax=Decimal(str(payload["tax"])),
        total=Decimal(str(payload["total"])),
    )
    for item in cart.items.select_related("product"):
        order.items.create(
            product=item.product,
            product_name=item.product.name,
            unit_price=item.unit_price,
            quantity=item.quantity,
        )
    services.clear(cart)
    return redirect("shop:order_confirmation", reference=order.reference)


# ── Fusion render-mode contract (fragment-path mirror of /fusion/*) ─────────


def render_mode(request: HttpRequest) -> JsonResponse:
    """GET /fusion/render-mode/ — report the active fusion render mode."""
    return render_mode_api(request)


def branding(request: HttpRequest) -> JsonResponse:
    """GET /fusion/branding/ — storefront branding (settings-driven)."""
    return branding_api(request)


def navigation(request: HttpRequest) -> JsonResponse:
    """GET /fusion/navigation/ — storefront nav items."""
    return navigation_api(request)


def assets(request: HttpRequest) -> JsonResponse:
    """GET /fusion/assets/ — FUSION_ASSETS manifest for bundle parity."""
    return assets_api(request)


@csrf_exempt
def session_mode(request: HttpRequest) -> JsonResponse:
    """Settings-UI toggle for the per-session render-mode preference.

    GET    → report current state
    POST   → store ``{"fusion_render_first": true|false}``
    DELETE → clear the stored preference

    ``@csrf_exempt`` must live on THIS URL-resolved view — Django's CSRF
    middleware only checks the view Django resolves from the URL pattern.
    """
    if request.method == "POST":
        return session_mode_set_api(request)
    if request.method == "DELETE":
        return session_mode_clear_api(request)
    return session_mode_get_api(request)
