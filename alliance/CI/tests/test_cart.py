from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from alliance.CI.models.cart import Cart, CartItem
from alliance.CI.services.cart_service import CartService
from apps.lms.models.courses.info import Course
from apps.lms.models.blocks.cart import CourseCartItem

User = get_user_model()

class CartServiceTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        # Create an instructor user if required
        self.instructor = User.objects.create_user(username='instructor', email='inst@example.com', password='password')
        self.course = Course.objects.create(
            title='Test Course',
            price=99.99,
            slug='test-course',
            instructor=self.instructor
        )

    def test_get_or_create_cart_authenticated(self):
        request = self.factory.get('/')
        request.user = self.user
        request.session = {}

        cart = CartService.get_or_create_cart(request)
        self.assertEqual(cart.user, self.user)
        self.assertEqual(Cart.objects.count(), 1)

    def test_get_or_create_cart_anonymous(self):
        request = self.factory.get('/')
        request.user = type('AnonymousUser', (), {'is_authenticated': False})()
        # Mock session
        class Session(dict):
            session_key = 'test_session_key'
            def create(self): pass
        request.session = Session()

        cart = CartService.get_or_create_cart(request)
        self.assertEqual(cart.session_key, 'test_session_key')
        self.assertIsNone(cart.user)
        self.assertEqual(Cart.objects.count(), 1)

    def test_add_item_to_cart(self):
        cart = Cart.objects.create(user=self.user)
        CartService.add_item(cart, self.course, quantity=2)

        self.assertEqual(cart.items.count(), 1)
        item = cart.items.first()
        self.assertEqual(item.course, self.course)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(float(item.price), 99.99)

    def test_merge_session_cart(self):
        # Setup session cart
        session_cart = {
            str(self.course.id): {
                'name': self.course.title,
                'price': str(self.course.price),
                'quantity': 1
            }
        }

        CartService.merge_session_cart_to_db(self.user, session_cart)

        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        item = cart.items.first()
        self.assertEqual(item.course, self.course)
