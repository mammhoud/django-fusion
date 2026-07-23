"""
Shop API — products, cart, orders (bolt-pattern adapter).

Matches the RTK Query slice at: store/api/endpoints/shop.ts
"""

import json
import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone

from www.api.data_adapter import (
    bolt_view,
    login_required,
    paginate_queryset,
    parse_body,
    get_image_url,
    get_user_display_name,
    paginated_response,
)

logger = logging.getLogger(__name__)


def _get_products(request):
    """Try to get products from available models, fallback to empty."""
    try:
        from plugins.products.models import Product

        queryset = Product.objects.filter(is_available=True)
        q = request.GET.get("search", "").strip()
        if q:
            queryset = queryset.filter(name__icontains=q)
        category = request.GET.get("category", "").strip()
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset.order_by("name")
    except Exception:
        return []


def _serialize_product(product) -> dict:
    """Serialize a product to the frontend-expected format."""
    images = []
    try:
        if product.image:
            images.append(product.image.url)
    except Exception:
        pass
    try:
        for img in product.images.all():
            images.append(img.image.url)
    except Exception:
        pass
    if not images:
        images.append("")

    return {
        "id": product.id,
        "name": product.name,
        "slug": getattr(product, "slug", ""),
        "description": getattr(product, "description", ""),
        "price": float(getattr(product, "price", 0)),
        "discounted_price": (
            float(product.discounted_price)
            if getattr(product, "discounted_price", None)
            else None
        ),
        "images": images,
        "category": getattr(product, "category_id", None),
        "category_name": getattr(product, "category_name", "")
        or str(getattr(product, "category", "")),
        "stock": getattr(product, "stock", 0) or getattr(product, "quantity", 0),
        "is_available": getattr(product, "is_available", True),
        "created_at": getattr(product, "created_at", timezone.now()).isoformat(),
    }


def _get_cart_items(request):
    """Get cart items from available cart service or session."""
    try:
        from plugins.products.services.cart_service import CartService

        cart = CartService.get_or_create_cart(request)
        items = []
        for item in cart.items.all():
            items.append(
                {
                    "id": item.id,
                    "product": item.product_id or str(item.id),
                    "product_name": item.product_name,
                    "product_image": "",
                    "product_price": float(item.price),
                    "quantity": item.quantity,
                    "subtotal": float(item.total_price),
                }
            )
        return items
    except Exception:
        return []


# ── Product Views ──


@bolt_view
def product_list(request):
    """GET /api/shop/products/ — List all shop products."""
    products = _get_products(request)
    page = int(request.GET.get("page", 1))
    items, pagination = (
        paginate_queryset(products, request)
        if hasattr(products, "count")
        else (
            products,
            {
                "page": 1,
                "per_page": 20,
                "total": len(products) if isinstance(products, list) else 0,
                "total_pages": 0,
            },
        )
    )
    return paginated_response(
        items, pagination, request, [_serialize_product(p) for p in items]
    )


@bolt_view
def product_detail(request, pk):
    """GET /api/shop/products/<pk>/ — Get single product details."""
    try:
        from plugins.products.models import Product

        product = get_object_or_404(Product, pk=pk)
    except Exception:
        return {"status": "error", "message": "Product not found"}, 404

    return {"status": "success", "data": _serialize_product(product)}


# ── Cart Views ──


@bolt_view
@login_required
def cart_view(request):
    """GET /api/shop/cart/ — Get current user's cart items."""
    items = _get_cart_items(request)
    return {"results": items, "count": len(items), "next": None, "previous": None}


@bolt_view
@login_required
def cart_add(request):
    """POST /api/shop/cart/add/ — Add item to cart."""
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    product_id = body.get("product_id")
    quantity = body.get("quantity", 1)

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
                "subtotal": (
                    float(item.total_price)
                    if hasattr(item, "total_price")
                    else float(product.price) * quantity
                ),
            },
        }
    except Exception as e:
        logger.error("Cart add error: %s", e)
        return {"status": "error", "message": "Failed to add item to cart"}, 500


@bolt_view
@login_required
def cart_item_view(request, item_id):
    """Handle PATCH (update quantity) and DELETE (remove item) on /api/shop/cart/<item_id>/."""
    if request.method == "PATCH":
        body = parse_body(request)
        if not body:
            return {"status": "error", "message": "Invalid request body"}, 400

        quantity = body.get("quantity", 1)
        try:
            from plugins.products.services.cart_service import CartService

            cart = CartService.get_or_create_cart(request)
            item = cart.items.get(id=item_id)
            item.quantity = quantity
            item.save(update_fields=["quantity"])
            return {
                "status": "success",
                "data": {
                    "id": item.id,
                    "quantity": item.quantity,
                    "subtotal": float(item.total_price),
                },
            }
        except Exception as e:
            logger.error("Cart update error: %s", e)
            return {"status": "error", "message": "Failed to update cart item"}, 500

    elif request.method == "DELETE":
        try:
            from plugins.products.services.cart_service import CartService

            cart = CartService.get_or_create_cart(request)
            cart.items.filter(id=item_id).delete()
            return {"status": "success", "message": "Item removed from cart"}
        except Exception as e:
            logger.error("Cart remove error: %s", e)
            return {"status": "error", "message": "Failed to remove cart item"}, 500


# ── Order Views ──


@bolt_view
@login_required
def orders_view(request):
    """GET/POST /api/shop/orders/ — List or create current user's orders."""
    if request.method == "POST":
        return order_create.__wrapped__.__wrapped__(request)
    return order_list.__wrapped__.__wrapped__(request)


@bolt_view
@login_required
def order_create(request):
    """POST /api/shop/orders/ — Create order from cart."""
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    shipping_address = body.get("shipping_address", "")
    payment_method = body.get("payment_method", "")

    try:
        from plugins.products.models import Order

        order = Order.objects.create(
            user=request.user,
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
                "payment_method": payment_method,
                "shipping_address": shipping_address,
                "created_at": (
                    order.created_at.isoformat()
                    if hasattr(order, "created_at")
                    else None
                ),
            },
        }
    except Exception as e:
        logger.error("Order create error: %s", e)
        return {"status": "error", "message": "Failed to create order"}, 500


@bolt_view
@login_required
def order_list(request):
    """GET /api/shop/orders/ — List user's orders."""
    try:
        from plugins.products.models import Order

        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        page = int(request.GET.get("page", 1))
        items, pagination = paginate_queryset(orders, request)

        return {
            **paginated_response(items, pagination, request, []),
            "results": [
                {
                    "id": o.id,
                    "items": [],
                    "total": float(o.total),
                    "status": o.status,
                    "payment_method": getattr(o, "payment_method", ""),
                    "shipping_address": getattr(o, "shipping_address", ""),
                    "created_at": (
                        o.created_at.isoformat() if hasattr(o, "created_at") else None
                    ),
                }
                for o in items
            ],
        }
    except Exception:
        return {"results": [], "count": 0, "next": None, "previous": None}
