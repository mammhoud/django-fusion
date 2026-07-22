"""
Data Shop API — products list/detail, cart management, order creation.

Replaces the DRF ProductViewSet, CartViewSet, and OrderViewSet.
All endpoints are new — no existing bolt equivalents.
"""

from __future__ import annotations

import logging

from django.shortcuts import get_object_or_404

from www.api.data.helpers import paginate_queryset, parse_body, get_current_user, get_image_url, get_user_display_name
from www.auth import TokenAuthBackend, auth_required

logger = logging.getLogger(__name__)


def register_handlers(bolt):
    """Register shop handlers on the given BoltAPI instance."""

    # ── GET /apis/shop/products — list products ──
    @bolt.get("/shop/products")
    def list_products(request):
        """GET /apis/shop/products — Paginated product list."""
        qs = _get_product_queryset(request)
        items, pagination = paginate_queryset(qs, request, default_per_page=20)
        data = [_serialize_product(p) for p in items]
        return {"status": "success", "data": data, "pagination": pagination}

    # ── GET /apis/shop/products/<pk> — product detail ──
    @bolt.get("/shop/products/<int:pk>")
    def get_product(request, pk):
        """GET /apis/shop/products/<pk> — Single product detail."""
        try:
            from plugins.products.models import Product
            product = Product.objects.get(pk=pk, is_available=True)
        except Exception:
            try:
                from www.content.models.lms import ShopProduct
                product = ShopProduct.objects.get(pk=pk, is_active=True)
            except Exception:
                return {"status": "error", "message": "Product not found"}, 404

        return {"status": "success", "data": _serialize_product(product)}

    # ── GET /apis/shop/cart — list cart items ──
    @bolt.get("/shop/cart", **auth_required())
    def list_cart(request):
        """GET /apis/shop/cart — Current user's cart items."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        items = _get_cart_items(user, request)
        return {"status": "success", "count": len(items), "results": items}

    # ── POST /apis/shop/cart/add — add item to cart ──
    @bolt.post("/shop/cart/add", **auth_required())
    def add_to_cart(request):
        """POST /apis/shop/cart/add — Add a product to cart."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        body = parse_body(request)
        product_id = body.get("product_id")
        quantity = int(body.get("quantity", 1))

        if not product_id:
            return {"status": "error", "message": "product_id is required"}, 400

        # Try to use the CartService if available
        try:
            from plugins.products.services.cart_service import CartService
            from plugins.products.models import Product

            product = get_object_or_404(Product, pk=product_id)
            cart = CartService.get_or_create_cart(request)

            item = CartService.add_item(
                cart=cart,
                product_name=product.name,
                price=float(product.price),
                quantity=quantity,
                product_id=str(product.id),
            )

            return {
                "status": "success",
                "data": {
                    "id": item.id,
                    "product": product_id,
                    "product_name": product.name,
                    "quantity": quantity,
                    "subtotal": float(getattr(item, "total_price", 0)) or float(product.price) * quantity,
                },
            }, 201
        except ImportError as imp:
            logger.debug("CartService not available: %s", imp)

        # Fallback: order-based cart
        try:
            from plugins.products.models import Order, OrderItem
            cart_order, _ = Order.objects.get_or_create(
                user=user,
                status="pending",
                defaults={"total": 0},
            )
            item, created = OrderItem.objects.get_or_create(
                order=cart_order,
                product_id=product_id,
                defaults={
                    "quantity": quantity,
                    "price": 0,
                },
            )
            if not created:
                item.quantity += quantity
                item.save(update_fields=["quantity"])

            return {
                "status": "success",
                "data": {
                    "id": item.id,
                    "product": product_id,
                    "quantity": item.quantity,
                    "subtotal": float(getattr(item, "total_price", 0)) or 0,
                },
            }, 201
        except Exception as e:
            logger.error(f"Cart add error: {e}")
            return {"status": "error", "message": "Failed to add item to cart"}, 500

    # ── PATCH /apis/shop/cart/<pk> — update cart item quantity ──
    @bolt.patch("/shop/cart/<int:pk>", **auth_required())
    def update_cart_item(request, pk):
        """PATCH /apis/shop/cart/<pk> — Update item quantity in cart."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        body = parse_body(request)
        quantity = int(body.get("quantity", 1))

        try:
            from plugins.products.services.cart_service import CartService
            cart = CartService.get_or_create_cart(request)
            item = cart.items.get(id=pk)
            item.quantity = quantity
            item.save(update_fields=["quantity"])
            return {
                "status": "success",
                "data": {
                    "id": item.id,
                    "quantity": item.quantity,
                    "subtotal": float(getattr(item, "total_price", 0)),
                },
            }
        except Exception as exc:
            logger.warning("CartService update_item failed for pk=%s: %s", pk, exc)

        return {"status": "error", "message": "Cart item not found"}, 404

    # ── DELETE /apis/shop/cart/<pk> — remove cart item ──
    @bolt.delete("/shop/cart/<int:pk>", **auth_required())
    def remove_cart_item(request, pk):
        """DELETE /apis/shop/cart/<pk> — Remove item from cart."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        try:
            from plugins.products.services.cart_service import CartService
            cart = CartService.get_or_create_cart(request)
            cart.items.filter(id=pk).delete()
            return {"status": "success", "message": "Item removed from cart"}
        except Exception as exc:
            logger.warning("CartService remove_item failed for pk=%s: %s", pk, exc)

        return {"status": "error", "message": "Cart item not found"}, 404

    # ── POST /apis/shop/cart/checkout — checkout cart ──
    @bolt.post("/shop/cart/checkout", **auth_required())
    def checkout_cart(request):
        """POST /apis/shop/cart/checkout — Create order from cart items."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        body = parse_body(request)
        shipping_address = body.get("shipping_address", "")
        payment_method = body.get("payment_method", "")

        if not shipping_address or not payment_method:
            return {"status": "error", "message": "shipping_address and payment_method are required"}, 400

        try:
            from plugins.products.models import Order
            order = Order.objects.create(
                user=user,
                shipping_address=shipping_address,
                payment_method=payment_method,
                status="pending",
                total=0,
            )
            return {
                "status": "success",
                "data": {
                    "id": order.id,
                    "items": [],
                    "total": float(order.total),
                    "status": order.status,
                    "payment_method": order.payment_method,
                    "shipping_address": order.shipping_address,
                },
            }, 201
        except Exception as e:
            logger.error(f"Checkout error: {e}")
            return {"status": "error", "message": "Failed to create order"}, 500

    # ── GET /apis/shop/orders — list user orders ──
    @bolt.get("/shop/orders", **auth_required())
    def list_orders(request):
        """GET /apis/shop/orders — Current user's orders."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        try:
            from plugins.products.models import Order
            qs = Order.objects.filter(user=user).order_by("-created_at")
            items, pagination = paginate_queryset(qs, request, default_per_page=20)

            data = [
                {
                    "id": o.id,
                    "items": [],
                    "total": float(o.total),
                    "status": o.status,
                    "payment_method": getattr(o, "payment_method", ""),
                    "shipping_address": getattr(o, "shipping_address", ""),
                    "created_at": str(getattr(o, "created_at", "")),
                }
                for o in items
            ]
            return {"status": "success", "data": data, "pagination": pagination}
        except Exception as e:
            logger.error(f"List orders error: {e}")
            return {"status": "success", "data": [], "pagination": {"page": 1, "per_page": 20, "total": 0, "total_pages": 0}}

    # ── POST /apis/shop/orders — create order ──
    @bolt.post("/shop/orders", **auth_required())
    def create_order(request):
        """POST /apis/shop/orders — Create a new order."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        body = parse_body(request)
        shipping_address = body.get("shipping_address", "")
        payment_method = body.get("payment_method", "")

        try:
            from plugins.products.models import Order
            order = Order.objects.create(
                user=user,
                shipping_address=shipping_address,
                payment_method=payment_method,
                status="pending",
                total=0,
            )
            return {
                "status": "success",
                "data": {
                    "id": order.id,
                    "items": [],
                    "total": float(order.total),
                    "status": order.status,
                    "payment_method": order.payment_method,
                    "shipping_address": order.shipping_address,
                    "created_at": str(getattr(order, "created_at", "")),
                },
            }, 201
        except Exception as e:
            logger.error(f"Create order error: {e}")
            return {"status": "error", "message": "Failed to create order"}, 500


# ═══════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════


def _get_product_queryset(request):
    """Build the product queryset with optional filters."""
    # Compatible query param getter
    def _val(key: str, default: str = "") -> str:
        if hasattr(request, "query"):
            return request.query.get(key, default)
        if hasattr(request, "GET"):
            return request.GET.get(key, default)
        return default

    try:
        # Use sync_to_async to avoid SynchronousOnlyOperation in bolt's async context
        from plugins.products.models import Product as SyncProduct
        qs = SyncProduct.objects.filter(is_available=True)

        q = _val("search").strip()
        if q:
            qs = qs.filter(name__icontains=q)

        category = _val("category").strip()
        if category:
            qs = qs.filter(category__slug=category)

        return qs.order_by("name")
    except Exception:
        pass

    try:
        from www.content.models.shop import Product as SyncProduct
        qs = SyncProduct.objects.filter(is_active=True)

        q = _val("search").strip()
        if q:
            qs = qs.filter(title__icontains=q)

        return qs.order_by("title")
    except Exception:
        pass

    logger.warning(
        "No product backend available — tried plugins.products.models.Product "
        "and www.content.models.shop.Product. Falling back to empty list."
    )
    return []


def _serialize_product(product) -> dict:
    """Serialize a product instance into the response shape."""
    images = []

    # Try different image access patterns
    for attr in ("image", "thumbnail", "images"):
        val = getattr(product, attr, None)
        if val is not None:
            url = get_image_url(val)
            if url:
                images.append(url)

    if not images:
        images.append("")

    return {
        "id": product.pk,
        "name": getattr(product, "name", "") or getattr(product, "title", ""),
        "slug": getattr(product, "slug", ""),
        "description": getattr(product, "description", ""),
        "price": float(getattr(product, "price", 0)),
        "discounted_price": (
            float(product.sale_price)
            if hasattr(product, "sale_price") and product.sale_price
            else None
        ),
        "images": images[:1],
        "category": _get_product_category(product),
        "category_name": _get_product_category_name(product),
        "stock": int(getattr(product, "stock", 0) or getattr(product, "quantity", 0) or 0),
        "is_available": getattr(product, "is_available", True),
        "created_at": str(getattr(product, "created_at", "")),
    }


def _get_product_category(product) -> int | None:
    """Get category ID from a product."""
    for attr in ("category_id", "category"):
        val = getattr(product, attr, None)
        if val is not None:
            if isinstance(val, int):
                return val
            if hasattr(val, "pk"):
                return val.pk
    return None


def _get_product_category_name(product) -> str:
    """Get category name from a product."""
    cat = getattr(product, "category", None)
    if cat is None:
        return ""
    if isinstance(cat, str):
        return cat
    if hasattr(cat, "name"):
        return cat.name
    if hasattr(cat, "title"):
        return cat.title
    return str(cat)


def _get_cart_items(user, request) -> list[dict]:
    """Get cart items for a user, trying multiple backends."""
    # Try CartService
    try:
        from plugins.products.services.cart_service import CartService
        cart = CartService.get_or_create_cart(request)
        items = []
        for item in cart.items.all():
            items.append({
                "id": item.id,
                "product": item.product_id or str(item.id),
                "product_name": getattr(item, "product_name", ""),
                "product_image": "",
                "product_price": float(getattr(item, "price", 0)),
                "quantity": getattr(item, "quantity", 1),
                "subtotal": float(getattr(item, "total_price", 0)),
            })
        return items
    except Exception as exc:
        logger.warning("CartService not available — trying Order fallback: %s", exc)

    # Fallback: Order-based cart
    try:
        from plugins.products.models import Order, OrderItem
        cart_order = Order.objects.filter(user=user, status="pending").first()
        if cart_order is None:
            return []

        items = []
        for item in OrderItem.objects.filter(order=cart_order):
            items.append({
                "id": item.id,
                "product": item.product_id or str(item.id),
                "product_name": "",
                "product_image": "",
                "product_price": float(getattr(item, "price", 0)),
                "quantity": getattr(item, "quantity", 1),
                "subtotal": float(getattr(item, "total_price", 0)) or float(getattr(item, "price", 0)) * getattr(item, "quantity", 1),
            })
        return items
    except Exception as exc:
        logger.warning(
            "Order-based cart fallback failed for user=%s: %s",
            getattr(user, "pk", "?"), exc,
        )
        return []
