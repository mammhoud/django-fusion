import logging

from django.conf import settings
from django_rseal.pipelines.services import CartServiceBase

from apps.lms.models.blocks.cart import CourseCartItem
from apps.lms.models.courses.info import Course
from core.CI.models.cart import Cart, CartItem

logger = logging.getLogger(__name__)


class CartService(CartServiceBase):
    """
    Cart service for ctc-research.com LMS.

    Delegates to django_rseal.pipelines.services.CartServiceBase
    """

    cart_model = Cart
    cart_item_model = CourseCartItem

    @classmethod
    def _merge_cart_item(cls, cart, product_id: str, item_data: dict):
        """
        Merge a single cart item from session to database.

        Args:
            cart: Cart instance
            product_id: Product identifier (course ID)
            item_data: Item data dictionary
        """
        try:
            # In this LMS, cart items are typically courses
            course = Course.objects.get(id=product_id)
            # Check if already in DB cart
            if not CourseCartItem.objects.filter(cart=cart, course=course).exists():
                CourseCartItem.objects.create(
                    cart=cart,
                    course=course,
                    quantity=item_data.get('quantity', 1),
                    price=float(item_data.get('price', course.price))
                )
        except Course.DoesNotExist:
            logger.warning(f"Attempted to merge non-existent course {product_id} into user cart.")
        except Exception as e:
            logger.error(f"Error merging session cart item {product_id}: {e}")
            raise e

    @classmethod
    def add_item(cls, cart, product, quantity: int = 1, **kwargs):
        """
        Add an item (Course) to the database cart.

        Args:
            cart: Cart instance
            product: Course to add
            quantity: Quantity to add
            **kwargs: Additional item data

        Returns:
            CourseCartItem instance
        """
        # For this LMS, we use CourseCartItem for courses
        item, created = CourseCartItem.objects.get_or_create(
            cart=cart,
            course=product,
            defaults={'price': product.price, 'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return item

    @classmethod
    def remove_from_cart(cls, user, item, **kwargs):
        """Remove item from cart."""
        cart = cls.get_or_create_cart(user._request if hasattr(user, '_request') else None)
        if isinstance(item, CourseCartItem):
            item.delete()
        elif isinstance(item, Course):
            CourseCartItem.objects.filter(cart=cart, course=item).delete()
        else:
            # Try to find by ID
            CourseCartItem.objects.filter(cart=cart, course__id=item).delete()

    @classmethod
    def clear_cart(cls, user, **kwargs):
        """Clear user's cart."""
        cart = cls.get_or_create_cart(user._request if hasattr(user, '_request') else None)
        cart.items.all().delete()
