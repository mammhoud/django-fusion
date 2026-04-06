import logging
from django.conf import settings
from alliance.CI.models.cart import Cart, CartItem
from alliance.CI.models.cart import Cart, CartItem

logger = logging.getLogger(__name__)

class CartService:
    @staticmethod
    def get_or_create_cart(request):
        """
        Retrieve or create a cart for the current session or user.
        """
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            # If we have a session cart, merge it
            if session_cart := request.session.get('cart'):
                CartService.merge_session_cart_to_db(request.user, session_cart)
                del request.session['cart']
                request.session.modified = True
            return cart
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            cart, created = Cart.objects.get_or_create(session_key=session_key)
            return cart

    @staticmethod
    def merge_session_cart_to_db(user, session_cart_data):
        """
        Merge items from a session-only cart (dict) into a user's database cart.
        """
        user_cart, _ = Cart.objects.get_or_create(user=user)

        for product_id, item_data in session_cart_data.items():
            try:
                # Check if already in DB cart
                if not CartItem.objects.filter(cart=user_cart, product_name=item_data.get('name')).exists():
                    CartItem.objects.create(
                        cart=user_cart,
                        product_name=item_data.get('name', 'Product'),
                        product_description=item_data.get('description', ''),
                        quantity=item_data.get('quantity', 1),
                        price=float(item_data.get('price', 0))
                    )
            except Exception as e:
                logger.error(f"Error merging session cart item {product_id}: {e}")

    @staticmethod
    def add_item(cart, product_name, price, quantity=1, description=""):
        """
        Add a generic item to the database cart.
        """
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_name=product_name,
            defaults={'price': price, 'quantity': quantity, 'product_description': description}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return item

    @staticmethod
    def get_cart_count(request):
        """
        Get total number of items in the cart.
        """
        if request.user.is_authenticated:
            try:
                return request.user.cart.total_items
            except AttributeError:
                return 0

        session_cart = request.session.get('cart', {})
        return sum(item.get('quantity', 1) for item in session_cart.values())
