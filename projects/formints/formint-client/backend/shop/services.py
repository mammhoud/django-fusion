"""Cart service — session-scoped cart helpers shared by views and templates."""
from decimal import Decimal

from .models import Cart, CartItem, Product

CART_SESSION_KEY = "purchase_cart_id"


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


def remove_item(cart: Cart, item_id: int) -> bool:
    deleted, _ = cart.items.filter(pk=item_id).delete()
    return deleted > 0


def clear(cart: Cart) -> None:
    cart.items.all().delete()


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
                "line_total": float(item.line_total),
                "image_url": item.product.image_url,
            }
        )
    subtotal = cart.subtotal
    tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
    return {
        "count": cart.item_count,
        "items": items,
        "subtotal": float(subtotal),
        "tax": float(tax),
        "total": float(subtotal + tax),
    }
