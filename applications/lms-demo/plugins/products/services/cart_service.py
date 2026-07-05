"""
CartService — concrete implementation for plugins.products.

Extends CartServiceBase from django-fusion with the project's Cart / CartItem
models.  Import this service everywhere instead of the old
``plugins.accounts.site.cart`` path.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Dict

from django.http import HttpRequest
from django_fusion.core.services import CartServiceBase

from plugins.products.models.cart import Cart, CartItem

logger = logging.getLogger(__name__)


class CartService(CartServiceBase):
    """Concrete cart service bound to the products plugin models."""

    cart_model = Cart
    cart_item_model = CartItem

    # ------------------------------------------------------------------
    # Convenience class-methods
    # ------------------------------------------------------------------

    @classmethod
    def get_cart_count(cls, request: HttpRequest) -> int:
        """Return total item units in the current cart."""
        if request.user.is_authenticated:
            cart = cls.get_or_create_cart(request)
            return cart.total_items
        session_cart: Dict[str, Any] = request.session.get("cart", {})
        return sum(item.get("quantity", 1) for item in session_cart.values())

    @classmethod
    def add_item(
        cls,
        cart: Cart,
        product_name: str,
        price: float | Decimal,
        quantity: int = 1,
        description: str = "",
        product_id: str = "",
    ) -> CartItem:
        """
        Add or increment a line item in *cart*.

        If an item with the same *product_id* (or *product_name* when
        *product_id* is empty) already exists, its quantity is incremented.
        """
        lookup = {"cart": cart}
        if product_id:
            lookup["product_id"] = product_id
        else:
            lookup["product_name"] = product_name

        item, created = CartItem.objects.get_or_create(
            **lookup,
            defaults={
                "product_name": product_name,
                "product_description": description,
                "price": Decimal(str(price)),
                "quantity": quantity,
                "product_id": product_id,
            },
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])
        return item

    @classmethod
    def _merge_cart_item(
        cls,
        cart: Cart,
        product_id: str,
        item_data: Dict[str, Any],
    ) -> None:
        """Merge a single session cart entry into the DB cart."""
        cls.add_item(
            cart=cart,
            product_name=item_data.get("name", ""),
            price=item_data.get("price", 0),
            quantity=item_data.get("quantity", 1),
            description=item_data.get("description", ""),
            product_id=product_id,
        )
