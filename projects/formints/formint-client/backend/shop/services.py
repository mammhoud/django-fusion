"""Cart service — session-scoped cart helpers shared by views and templates."""
from decimal import Decimal

from django.utils import timezone

from .models import Cart, CartItem, Product, PromoCode

CART_SESSION_KEY = "purchase_cart_id"
PROMO_SESSION_KEY = "purchase_promo_code"
TAX_RATE = Decimal("0.10")


def get_or_create_cart(request) -> Cart:
    """Return the request's cart, creating it (and storing its id in the
    session) on first use."""
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).order_by("-updated_at").first()
        if cart:
            request.session[CART_SESSION_KEY] = cart.pk
            return cart
    cart_id = request.session.get(CART_SESSION_KEY)
    if cart_id:
        cart = Cart.objects.filter(pk=cart_id).first()
        if cart:
            return cart
    cart = Cart.objects.create(
        session_key=request.session.session_key,
        user=request.user if request.user.is_authenticated else None,
    )
    request.session[CART_SESSION_KEY] = cart.pk
    return cart


def merge_session_cart_to_user(request) -> Cart:
    """After login, adopt the guest cart (if any) under the authenticated user."""
    cart = get_or_create_cart(request)
    if request.user.is_authenticated and cart.user != request.user:
        cart.user = request.user
        cart.save()
    return cart


def add_item(cart: Cart, product: Product, quantity: int = 1) -> CartItem:
    quantity = max(1, int(quantity))
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"unit_price": product.price, "quantity": quantity},
    )
    if not created:
        item.quantity += quantity
        item.save(update_fields=["quantity"])
    return item


def set_quantity(cart: Cart, item_id: int, quantity: int) -> CartItem | None:
    item = cart.items.filter(pk=item_id).first()
    if not item:
        return None
    if quantity <= 0:
        item.delete()
        return None
    item.quantity = int(quantity)
    item.save(update_fields=["quantity"])
    return item


def set_note(cart: Cart, item_id: int, note: str) -> CartItem | None:
    """Attach a per-item instruction ("no onions")."""
    item = cart.items.filter(pk=item_id).first()
    if not item:
        return None
    item.note = (note or "").strip()[:200]
    item.save(update_fields=["note"])
    return item


def remove_item(cart: Cart, item_id: int) -> bool:
    deleted, _ = cart.items.filter(pk=item_id).delete()
    return deleted > 0


def clear(cart: Cart) -> None:
    cart.items.all().delete()


# ── Promo codes ────────────────────────────────────────────────────────────


def resolve_promo(code: str) -> PromoCode | None:
    """Return the promo if it exists and is usable right now, else None."""
    if not code:
        return None
    promo = PromoCode.objects.filter(code__iexact=code.strip()).first()
    if promo and promo.is_usable:
        return promo
    return None


def apply_discount(subtotal: Decimal, promo: PromoCode | None) -> Decimal:
    """Discount amount for a subtotal (0 when no/expired promo)."""
    if not promo:
        return Decimal("0.00")
    return promo.discount_for(subtotal)


def get_session_promo(request) -> PromoCode | None:
    """Promo stored on the session, re-validated at read time."""
    code = request.session.get(PROMO_SESSION_KEY, "")
    return resolve_promo(code)


def set_session_promo(request, code: str) -> PromoCode | None:
    """Validate + persist a promo on the session. Returns None when invalid."""
    promo = resolve_promo(code)
    if promo:
        request.session[PROMO_SESSION_KEY] = promo.code
    else:
        request.session.pop(PROMO_SESSION_KEY, None)
    return promo


def clear_session_promo(request) -> None:
    request.session.pop(PROMO_SESSION_KEY, None)


def cart_payload(cart: Cart) -> dict:
    """JSON-friendly cart snapshot used by the frontend + templates."""
    items = []
    for item in cart.items.select_related("product"):
        items.append(
            {
                "id": item.pk,
                "product_id": item.product_id,
                "name": item.product.name,
                "slug": item.product.slug,
                "unit_price": float(item.unit_price),
                "quantity": item.quantity,
                "note": item.note,
                "line_total": float(item.line_total),
                "image_url": item.product.image_url,
            }
        )
    subtotal = cart.subtotal
    discount = apply_discount(subtotal, None)  # cart-level promo lives at checkout
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
    return {
        "count": cart.item_count,
        "items": items,
        "subtotal": float(subtotal),
        "tax": float(tax),
        "total": float(subtotal + tax),
    }


def checkout_totals(cart: Cart, promo: PromoCode | None) -> dict:
    """Checkout totals with the session promo applied.

    Discount applies to the subtotal; tax is computed on the discounted
    amount (tax_on = subtotal - discount).
    """
    subtotal = cart.subtotal
    discount = apply_discount(subtotal, promo)
    taxable = max(subtotal - discount, Decimal("0"))
    tax = (taxable * TAX_RATE).quantize(Decimal("0.01"))
    total = (taxable + tax).quantize(Decimal("0.01"))
    return {
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "promo_code": promo.code if promo else "",
    }
