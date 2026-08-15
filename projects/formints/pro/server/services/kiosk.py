"""
POS Full — Self-checkout Kiosk service (P3).

Self-service kiosk mode: a touchscreen guest scans/browses the catalog,
builds a cart on a ``KioskSession``, and checks out. Checkout reuses the
canonical ``sale_checkout`` surface (the same atomic Sale + SaleItem +
KitchenTicket path the cashier screen uses) — this service never reimplements
sale creation; it drives the existing endpoint with the kiosk's cart payload.

Scope per the roadmap: **self-service kiosk mode** (Professional/SaaS).
"""

from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import Any

from django.utils import timezone

from models.kiosk import KioskCartItem, KioskSession
from models.pos import Product


class KioskError(Exception):
    """Raised for kiosk domain violations (empty cart, unknown product, …)."""


def catalog(category_slug: str = "") -> dict[str, Any]:
    """Active products grouped by category for the touchscreen.

    ``?category=<slug>`` narrows to one category; empty returns everything.
    Each product carries id/name/price/stock-availability so the UI can
    disable out-of-stock tiles.
    """
    from models.pos import Category

    products = Product.objects.filter(is_active=True).select_related("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)
    products = products.order_by("category__display_order", "category__name", "name")

    grouped: dict[str, list[dict[str, Any]]] = {}
    for product in products:
        cat_name = product.category.name if product.category else "Other"
        grouped.setdefault(cat_name, []).append({
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "image_url": product.image_url or "",
            "border_color": product.border_color or "",
            "in_stock": product.stock_quantity is None or product.stock_quantity > 0,
            "stock_quantity": product.stock_quantity,
        })

    categories = list(
        Category.objects.filter(is_active=True)
        .order_by("display_order", "name")
        .values("id", "name", "slug")
    )
    return {
        "categories": categories,
        "groups": grouped,
        "product_count": sum(len(v) for v in grouped.values()),
    }


def start_session(session_key: str = "", name: str = "") -> KioskSession:
    """Create a new open kiosk session (or reuse an open one with the same key)."""
    key = (session_key or "").strip() or f"kiosk-{uuid.uuid4().hex[:10]}"
    existing = KioskSession.objects.filter(session_key=key).first()
    if existing:
        if existing.status == "open":
            return existing
        # Reuse the key with a fresh open session.
        existing.status = "open"
        existing.sale = None
        existing.closed_at = None
        existing.payment_method = "card"
        existing.save(update_fields=["status", "sale", "closed_at", "payment_method"])
        return existing
    return KioskSession.objects.create(session_key=key, name=name)


def get_session(session_key: str) -> KioskSession | None:
    return KioskSession.objects.filter(session_key=session_key).first()


def _require_open(session: KioskSession) -> None:
    if session.status != "open":
        raise KioskError(f"Session is {session.status}, not open")


def add_item(session: KioskSession, product_id: int, quantity: int = 1) -> KioskCartItem:
    """Add (or increment) a product in the session cart with stock validation."""
    _require_open(session)
    if quantity <= 0:
        raise KioskError("quantity must be positive")
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise KioskError(f"Product {product_id} not found")
    if not product.is_active:
        raise KioskError(f"'{product.name}' is not available")
    if product.stock_quantity is not None and product.stock_quantity < quantity:
        raise KioskError(
            f"Insufficient stock for '{product.name}': "
            f"requested {quantity}, available {product.stock_quantity}"
        )

    existing = session.cart_items.filter(product_id=product_id).first()
    if existing:
        new_qty = existing.quantity + quantity
        if product.stock_quantity is not None and new_qty > product.stock_quantity:
            raise KioskError(
                f"Cart exceeds stock for '{product.name}': "
                f"{new_qty} requested, {product.stock_quantity} available"
            )
        existing.quantity = new_qty
        existing.save(update_fields=["quantity"])
        return existing

    return KioskCartItem.objects.create(
        session=session,
        product=product,
        product_name=product.name,
        quantity=quantity,
        unit_price=product.price,
    )


def set_quantity(session: KioskSession, product_id: int, quantity: int) -> KioskCartItem:
    """Set a cart line to an exact quantity (0 removes the line)."""
    _require_open(session)
    item = session.cart_items.filter(product_id=product_id).first()
    if item is None:
        raise KioskError(f"Product {product_id} is not in the cart")
    if quantity <= 0:
        item.delete()
        raise KioskError(f"Product {product_id} removed from the cart")
    if item.product and item.product.stock_quantity is not None \
            and quantity > item.product.stock_quantity:
        raise KioskError(
            f"Insufficient stock for '{item.product_name}': "
            f"requested {quantity}, available {item.product.stock_quantity}"
        )
    item.quantity = quantity
    item.save(update_fields=["quantity"])
    return item


def remove_item(session: KioskSession, product_id: int) -> None:
    _require_open(session)
    session.cart_items.filter(product_id=product_id).delete()


def clear_cart(session: KioskSession) -> None:
    _require_open(session)
    session.cart_items.all().delete()


def cart_summary(session: KioskSession) -> dict[str, Any]:
    """Cart rows + computed subtotal/tax/total (standard 8 % tax default)."""
    rows = []
    subtotal = Decimal("0")
    for item in session.cart_items.select_related("product"):
        subtotal += Decimal(str(item.unit_price)) * item.quantity
        rows.append({
            "product_id": item.product_id,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "line_total": round(float(item.unit_price) * item.quantity, 2),
        })
    tax_amount = round(subtotal * Decimal("0.08"), 2)
    total = round(subtotal + tax_amount, 2)
    return {
        "session_key": session.session_key,
        "items": rows,
        "item_count": sum(r["quantity"] for r in rows),
        "subtotal": float(subtotal),
        "tax_amount": float(tax_amount),
        "total": float(total),
    }


def checkout(session: KioskSession, payment_method: str = "card") -> dict[str, Any]:
    """Check the kiosk cart out through the canonical ``sale_checkout`` path.

    Builds the exact payload ``POST /sales/`` expects and forwards it through
    the view (via Django's test RequestFactory) so stock deduction, the
    atomic Sale/SaleItem creation, and KitchenTicket routing stay in one
    place. On success the session links the sale and closes itself.
    """
    _require_open(session)
    items = list(session.cart_items.select_related("product"))
    if not items:
        raise KioskError("Cart is empty")

    payload_items = []
    subtotal = Decimal("0")
    for item in items:
        payload_items.append({
            "product_id": item.product_id,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "line_total": round(float(item.unit_price) * item.quantity, 2),
        })
        subtotal += Decimal(str(item.unit_price)) * item.quantity
    tax_amount = round(subtotal * Decimal("0.08"), 2)
    payload = {
        "items": payload_items,
        "subtotal": float(subtotal),
        "tax_amount": float(tax_amount),
        "total": float(subtotal + tax_amount),
        "payment_method": payment_method or session.payment_method or "card",
        "status": "completed",
        "notes": f"Kiosk checkout — {session.name or session.session_key}",
        "create_kitchen_ticket": True,
        "order_type": "takeaway",
    }

    from django.test import RequestFactory
    from views_django import sale_checkout

    request = RequestFactory().post(
        "/sales/", data=json.dumps(payload), content_type="application/json"
    )
    response = sale_checkout(request)
    if response.status_code != 201:
        body = json.loads(response.content) if response.content else {"error": "unknown"}
        raise KioskError(body.get("error", f"checkout failed ({response.status_code})"))

    result = json.loads(response.content)
    session.sale_id = result["sale_id"]
    session.status = "checked_out"
    session.payment_method = payment_method or session.payment_method or "card"
    session.closed_at = timezone.now()
    session.save(update_fields=["sale_id", "status", "payment_method", "closed_at"])

    return {
        "session_key": session.session_key,
        "sale_id": result["sale_id"],
        "total": result["total"],
        "item_count": result["item_count"],
        "kitchen_ticket_id": (result.get("kitchen_ticket") or {}).get("id"),
        "status": session.status,
    }


def cancel_session(session: KioskSession) -> KioskSession:
    _require_open(session)
    session.cart_items.all().delete()
    session.status = "cancelled"
    session.closed_at = timezone.now()
    session.save(update_fields=["status", "closed_at"])
    return session


def kiosk_stats() -> dict[str, Any]:
    """Light session/checkout stats for the kiosk dashboard tile."""
    from django.db.models import Count

    counts = dict(
        KioskSession.objects.values("status")
        .annotate(n=Count("id")).values_list("status", "n")
    )
    checked_out = KioskSession.objects.filter(status="checked_out").count()
    return {
        "open": counts.get("open", 0),
        "checked_out": checked_out,
        "cancelled": counts.get("cancelled", 0),
        "total_sales": checked_out,
    }
