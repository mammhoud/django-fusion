"""
Cart & Checkout views for the products plugin.

All views are HTMX-friendly: they return HTML partials when called via
HTMX and full pages otherwise.
"""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django_osoul.site import PageHandler

from plugins.products.services.cart_service import CartService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


def _build_db_items(cart) -> list[dict]:
    items = []
    for item in cart.items.all():
        items.append({
            "id": str(item.id),
            "product": {
                "id": item.product_id or str(item.id),
                "name": item.product_name,
                "description": item.product_description,
                "price": float(item.price),
            },
            "quantity": item.quantity,
            "total_price": float(item.total_price),
        })
    return items


def _build_session_items(session_cart: dict) -> list[dict]:
    items = []
    for product_id, item_data in session_cart.items():
        items.append({
            "id": product_id,
            "product": {
                "id": product_id,
                "name": item_data.get("name", str(_("Product"))),
                "description": item_data.get("description", ""),
                "price": float(item_data.get("price", 0)),
                "image": item_data.get("image"),
            },
            "quantity": item_data.get("quantity", 1),
            "total_price": float(item_data.get("price", 0)) * item_data.get("quantity", 1),
        })
    return items


def _get_cart_items(request: HttpRequest) -> list[dict]:
    if request.user.is_authenticated:
        return _build_db_items(CartService.get_or_create_cart(request))
    return _build_session_items(request.session.get("cart", {}))


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class CartView(PageHandler):
    """Display the shopping cart (full page or HTMX partial)."""

    page_title = _("Shopping Cart")
    template_name = "products/cart/items.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart_items"] = _get_cart_items(request)
        return context


class CartCountView(View):
    """Return the cart item count as an HTML partial."""

    def get(self, request: HttpRequest) -> HttpRequest:
        count = CartService.get_cart_count(request)
        return render(request, "products/cart/count.html", {"count": count})


class CartSubtotalView(View):
    """Return the cart subtotal as an HTML partial."""

    def get(self, request: HttpRequest) -> HttpRequest:
        if request.user.is_authenticated:
            cart = CartService.get_or_create_cart(request)
            subtotal = float(cart.total_price)
        else:
            session_cart = request.session.get("cart", {})
            subtotal = sum(
                float(v.get("price", 0)) * v.get("quantity", 1)
                for v in session_cart.values()
            )
        return render(request, "products/cart/subtotal.html", {"subtotal": subtotal})


class CartUpdateQuantityView(View):
    """Increase or decrease a cart item's quantity."""

    def post(self, request: HttpRequest, item_id: str) -> HttpRequest:
        action = request.POST.get("action", "increase")

        if request.user.is_authenticated:
            cart = CartService.get_or_create_cart(request)
            try:
                item = cart.items.get(id=item_id)
                if action == "increase":
                    item.quantity += 1
                elif action == "decrease":
                    item.quantity = max(1, item.quantity - 1)
                item.save(update_fields=["quantity"])
            except Exception:
                pass
        else:
            session_cart = request.session.get("cart", {})
            if item_id in session_cart:
                if action == "increase":
                    session_cart[item_id]["quantity"] = session_cart[item_id].get("quantity", 1) + 1
                elif action == "decrease":
                    session_cart[item_id]["quantity"] = max(1, session_cart[item_id].get("quantity", 1) - 1)
                request.session["cart"] = session_cart
                request.session.modified = True

        return render(request, "products/cart/items.html", {"cart_items": _get_cart_items(request)})


class CartRemoveItemView(View):
    """Remove a single item from the cart."""

    def delete(self, request: HttpRequest, item_id: str) -> HttpRequest:
        if request.user.is_authenticated:
            cart = CartService.get_or_create_cart(request)
            cart.items.filter(id=item_id).delete()
        else:
            session_cart = request.session.get("cart", {})
            session_cart.pop(item_id, None)
            request.session["cart"] = session_cart
            request.session.modified = True

        return render(request, "products/cart/items.html", {"cart_items": _get_cart_items(request)})


class CartAddItemView(View):
    """Add an item to the cart and return the updated count."""

    def post(self, request: HttpRequest) -> JsonResponse:
        product_name = request.POST.get("product_name", str(_("Product")))
        product_id = request.POST.get("product_id", "")
        price = float(request.POST.get("price", 0))
        quantity = int(request.POST.get("quantity", 1))
        description = request.POST.get("description", "")

        if request.user.is_authenticated:
            cart = CartService.get_or_create_cart(request)
            CartService.add_item(
                cart=cart,
                product_name=product_name,
                price=price,
                quantity=quantity,
                description=description,
                product_id=product_id,
            )
            count = cart.total_items
        else:
            session_cart = request.session.get("cart", {})
            key = product_id or product_name
            if key in session_cart:
                session_cart[key]["quantity"] += quantity
            else:
                session_cart[key] = {
                    "name": product_name,
                    "price": price,
                    "quantity": quantity,
                    "description": description,
                }
            request.session["cart"] = session_cart
            request.session.modified = True
            count = sum(v.get("quantity", 1) for v in session_cart.values())

        return JsonResponse({
            "status": "success",
            "message": str(_("Item added to cart")),
            "count": count,
        })


class CheckoutView(PageHandler):
    """Checkout summary page."""

    page_title = _("Checkout")
    template_name = "products/checkout.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = _get_cart_items(request)
        subtotal = sum(item["total_price"] for item in cart_items)
        context.update({
            "cart_items": cart_items,
            "subtotal": subtotal,
            "total": subtotal,
        })
        return context
