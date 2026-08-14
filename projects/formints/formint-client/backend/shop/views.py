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
    "orders_api",
    "order_create_api",
    "order_detail_api",
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


def _order_payload(order: Order, *, detail: bool = False) -> dict:
    """Serialize an order for the POS API (decimal-safe string amounts)."""
    payload = {
        "id": order.pk,
        "reference": order.reference,
        "customer_name": order.customer_name,
        "status": order.status,
        "order_type": order.order_type,
        "total_amount": str(order.total),
        "currency": "$",
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "id": i.pk,
                "product_name": i.product_name,
                "unit_price": str(i.unit_price),
                "quantity": i.quantity,
                "subtotal": str(i.line_total),
            }
            for i in order.items.all()
        ],
    }
    if detail:
        payload.update(
            {
                "customer_email": order.customer_email,
                "customer_phone": order.customer_phone,
                "notes": order.notes,
                "subtotal": str(order.subtotal),
                "tax": str(order.tax),
            }
        )
    return payload


@csrf_exempt
def orders_api(request: HttpRequest) -> JsonResponse:
    """GET /api/orders/ → recent orders JSON; POST /api/orders/ → create.

    Method dispatch mirrors the ``session_mode`` contract: the same URL
    serves the POS client's list (GET) and register submission (POST).
    Amounts are strings (decimal-safe), matching the catalog convention.

    ``@csrf_exempt`` must live on THIS URL-resolved view (same rule as
    ``session_mode``) — the POS client posts cross-origin without a token.
    """
    if request.method == "POST":
        return order_create_api(request)
    if request.method != "GET":
        return JsonResponse({"error": "method not allowed"}, status=405)
    orders = Order.objects.prefetch_related("items").order_by("-created_at")[:50]
    return JsonResponse(
        {"orders": [_order_payload(o) for o in orders]}
    )


@require_POST
def order_create_api(request: HttpRequest) -> JsonResponse:
    """POST /api/orders/ — create an order directly from the POS register.

    JSON body:
        {
          "items": [{"product_id": 3, "quantity": 2}, ...],
          "order_type": "dine_in" | "takeaway" | "delivery",
          "customer_name": "...",
          "customer_email": "...",
          "customer_phone": "...",
          "notes": "..."
        }

    Totals are recomputed server-side from current catalog prices (never
    trusted from the client) with the same 10% tax as the session-cart
    checkout, and serialized decimal-safe (strings) via ``_order_payload``.

    CSRF is handled on the URL-resolved dispatcher (``orders_api``) — the
    POS client posts cross-origin without a token, same trust boundary as
    the storefront's authenticated cart.
    """
    import json

    try:
        body = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"error": "invalid JSON body"}, status=400)

    raw_items = body.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        return JsonResponse({"error": "items must be a non-empty list"}, status=400)

    # Resolve products once; reject unknown ids up front so nothing partial
    # is persisted.
    quantities: list[tuple[Product, int]] = []
    for entry in raw_items:
        if not isinstance(entry, dict):
            return JsonResponse({"error": "each item must be an object"}, status=400)
        product_id = entry.get("product_id")
        quantity = entry.get("quantity", 1)
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return JsonResponse({"error": "quantity must be an integer"}, status=400)
        if quantity < 1:
            return JsonResponse({"error": "quantity must be at least 1"}, status=400)
        product = (
            Product.objects.filter(pk=product_id, is_available=True)
            .select_related("category")
            .first()
        )
        if product is None:
            return JsonResponse(
                {"error": f"unknown or unavailable product_id: {product_id}"}, status=400
            )
        quantities.append((product, quantity))

    order_type = body.get("order_type", Order.OrderType.TAKEAWAY)
    if order_type not in Order.OrderType.values:
        order_type = Order.OrderType.TAKEAWAY

    subtotal = sum(p.price * q for p, q in quantities)
    tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        customer_name=str(body.get("customer_name", "")).strip() or "Guest",
        customer_email=str(body.get("customer_email", "")).strip(),
        customer_phone=str(body.get("customer_phone", "")).strip(),
        order_type=order_type,
        notes=str(body.get("notes", "")).strip(),
        subtotal=subtotal,
        tax=tax,
        total=subtotal + tax,
    )
    for product, quantity in quantities:
        order.items.create(
            product=product,
            product_name=product.name,
            unit_price=product.price,
            quantity=quantity,
        )
    return JsonResponse(_order_payload(order, detail=True), status=201)


@require_GET
def order_detail_api(request: HttpRequest, pk: int) -> JsonResponse:
    """GET /api/orders/<pk>/ — full detail for one order.

    The POS Orders view expands a card to fetch this: adds customer contact,
    notes and the subtotal/tax breakdown on top of the list payload.
    """
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk)
    return JsonResponse(_order_payload(order, detail=True))


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
