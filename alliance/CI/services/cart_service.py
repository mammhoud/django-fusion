import logging

from django.conf import settings
from django_rseal.pipelines.services import CartServiceBase

from alliance.CI.models.cart import Cart, CartItem

logger = logging.getLogger(__name__)


class CartService(CartServiceBase):
    """
    Cart service for structa.cloud alliance.

    Delegates to django_rseal.pipelines.services.CartServiceBase
    """

    cart_model = Cart
    cart_item_model = CartItem

    @classmethod
    def _merge_cart_item(cls, cart, product_id: str, item_data: dict):
        """
        Merge a single cart item from session to database.

        Args:
            cart: Cart instance
            product_id: Product identifier
            item_data: Item data dictionary
        """
        try:
            # Check if already in DB cart
            if not CartItem.objects.filter(cart=cart, product_name=item_data.get('name')).exists():
                CartItem.objects.create(
                    cart=cart,
                    product_name=item_data.get('name', 'Product'),
                    product_description=item_data.get('description', ''),
                    quantity=item_data.get('quantity', 1),
                    price=float(item_data.get('price', 0))
                )
        except Exception as e:
            logger.error(f"Error merging session cart item {product_id}: {e}")

    @classmethod
    def add_item(cls, cart, product, quantity: int = 1, **kwargs):
        """
        Add an item to the database cart.

        Args:
            cart: Cart instance
            product: Product to add (could be string name or dict with product data)
            quantity: Quantity to add
            **kwargs: Additional item data

        Returns:
            CartItem instance
        """
        # Handle different product input types
        if isinstance(product, str):
            product_name = product
            price = kwargs.get('price', 0)
            description = kwargs.get('description', '')
        elif isinstance(product, dict):
            product_name = product.get('name', 'Product')
            price = product.get('price', 0)
            description = product.get('description', '')
        else:
            # Assume it's a product object with name, price, description attributes
            product_name = getattr(product, 'name', 'Product')
            price = getattr(product, 'price', 0)
            description = getattr(product, 'description', '')

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_name=product_name,
            defaults={'price': price, 'quantity': quantity, 'product_description': description}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return item

    @classmethod
    def remove_from_cart(cls, user, item, **kwargs):
        """Remove item from cart."""
        cart = cls.get_or_create_cart(user._request if hasattr(user, '_request') else None)
        if isinstance(item, CartItem):
            item.delete()
        elif isinstance(item, str):
            CartItem.objects.filter(cart=cart, product_name=item).delete()
        else:
            # Try to find by ID
            CartItem.objects.filter(cart=cart, id=item).delete()

    @classmethod
    def clear_cart(cls, user, **kwargs):
        """Clear user's cart."""
        cart = cls.get_or_create_cart(user._request if hasattr(user, '_request') else None)
        cart.items.all().delete()
