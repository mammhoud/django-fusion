"""
CartServiceBase: Base class for cart service implementations.

Canonical import: from django_fusion.services.cart import CartServiceBase
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CartServiceBase:
    """Base class for cart service implementations."""

    cart_model = None  # Injected by subclass
    cart_item_model = None  # Injected by subclass

    @classmethod
    def get_or_create_cart(cls, request) -> Any:
        """
        Retrieve or create a cart for the current session or user.

        Args:
            request: Django HttpRequest object

        Returns:
            Cart instance
        """
        if cls.cart_model is None:
            raise NotImplementedError("cart_model must be set by subclass")

        if request.user.is_authenticated:
            cart, created = cls.cart_model.objects.get_or_create(user=request.user)
            # If we have a session cart, merge it
            if session_cart := request.session.get('cart'):
                cls.merge_session_cart_to_db(request.user, session_cart)
                del request.session['cart']
                request.session.modified = True
            return cart
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            cart, created = cls.cart_model.objects.get_or_create(session_key=session_key)
            return cart

    @classmethod
    def merge_session_cart_to_db(cls, user, session_cart_data: dict[str, Any]) -> None:
        """
        Merge items from a session-only cart (dict) into a user's database cart.

        Args:
            user: User instance
            session_cart_data: Dictionary of session cart items
        """
        if cls.cart_model is None or cls.cart_item_model is None:
            raise NotImplementedError("cart_model and cart_item_model must be set by subclass")

        user_cart, _ = cls.cart_model.objects.get_or_create(user=user)

        for product_id, item_data in session_cart_data.items():
            try:
                # Check if already in DB cart
                # Subclasses should implement their own logic for checking duplicates
                cls._merge_cart_item(user_cart, product_id, item_data)
            except Exception as e:
                logger.error(f"Error merging session cart item {product_id}: {e}")

    @classmethod
    def _merge_cart_item(cls, cart, product_id: str, item_data: dict[str, Any]) -> None:
        """
        Merge a single cart item from session to database.
        Subclasses should override this method.

        Args:
            cart: Cart instance
            product_id: Product identifier
            item_data: Item data dictionary
        """
        raise NotImplementedError("Subclasses must implement _merge_cart_item")

    @classmethod
    def add_item(cls, cart, product, quantity: int = 1, **kwargs) -> Any:
        """
        Add an item to the cart.

        Args:
            cart: Cart instance
            product: Product to add (could be model instance or identifier)
            quantity: Quantity to add
            **kwargs: Additional item data

        Returns:
            CartItem instance
        """
        if cls.cart_item_model is None:
            raise NotImplementedError("cart_item_model must be set by subclass")

        # Subclasses should implement their own add_item logic
        raise NotImplementedError("Subclasses must implement add_item")

    @classmethod
    def get_cart_count(cls, request) -> int:
        """
        Get total number of items in the cart.

        Args:
            request: Django HttpRequest object

        Returns:
            Total item count
        """
        if request.user.is_authenticated:
            try:
                return request.user.cart.total_items
            except AttributeError:
                return 0

        session_cart = request.session.get('cart', {})
        return sum(item.get('quantity', 1) for item in session_cart.values())

    @classmethod
    def add_to_cart(cls, user, item, quantity: int, **kwargs):
        """Add item to cart (legacy method name)."""
        # For backward compatibility
        cart = cls.get_or_create_cart(user._request if hasattr(user, '_request') else None)
        return cls.add_item(cart, item, quantity, **kwargs)

    @classmethod
    def remove_from_cart(cls, user, item, **kwargs):
        """Remove item from cart."""
        if cls.cart_model is None or cls.cart_item_model is None:
            raise NotImplementedError("cart_model and cart_item_model must be set by subclass")
        raise NotImplementedError("Subclasses must implement remove_from_cart")

    @classmethod
    def get_cart(cls, user, **kwargs):
        """Get user's cart (legacy method name)."""
        # For backward compatibility
        return cls.get_or_create_cart(user._request if hasattr(user, '_request') else None)

    @classmethod
    def clear_cart(cls, user, **kwargs):
        """Clear user's cart."""
        if cls.cart_model is None:
            raise NotImplementedError("cart_model must be set by subclass")
        raise NotImplementedError("Subclasses must implement clear_cart")
