import json
import logging

from core.CI.services.cart_service import CartService
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django_rseal.services.commerce.payments import PayPalGateway, StripeGateway

logger = logging.getLogger(__name__)

class BasePaymentInitView(View):
    gateway_class = None

    def get_amount_and_metadata(self, request, **kwargs):
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        try:
            amount, metadata = self.get_amount_and_metadata(request, **kwargs)
            gateway = self.gateway_class()
            payment_data = gateway.initialize_payment(
                amount=amount,
                metadata=metadata
            )
            return JsonResponse(payment_data)
        except Exception as e:
            logger.error(f"Payment initialization failed: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class StripeInitView(BasePaymentInitView):
    gateway_class = StripeGateway

    def get_amount_and_metadata(self, request, **kwargs):
        # This implementation still needs to know about the product.
        # We'll use a generic approach if possible, or expect kwargs to have enough info.
        # For now, we'll keep it compatible with the slug passing if it's for a course.
        # Project-specific imports removed
        course = get_object_or_404(Course, slug=kwargs.get('slug'))
        return course.price, {
            'course_id': str(course.id),
            'user_id': str(request.user.id) if request.user.is_authenticated else 'guest',
            'email': request.user.email if request.user.is_authenticated else ''
        }

class PayPalInitView(BasePaymentInitView):
    gateway_class = PayPalGateway

    def get_amount_and_metadata(self, request, **kwargs):
        # Project-specific imports removed
        course = get_object_or_404(Course, slug=kwargs.get('slug'))
        return course.price, {
            'course_id': str(course.id),
            'user_id': str(request.user.id) if request.user.is_authenticated else 'guest'
        }

class CartStripeInitView(BasePaymentInitView):
    gateway_class = StripeGateway

    def get_amount_and_metadata(self, request, **kwargs):
        cart = CartService.get_or_create_cart(request)
        if request.user.is_authenticated:
            amount = cart.total_price
        else:
            # Fallback for session cart
            session_cart = request.session.get('cart', {})
            amount = sum(float(i['price']) * i['quantity'] for i in session_cart.values())

        if amount <= 0:
             raise ValueError("Cart is empty or has zero value")

        return amount, {
            'cart_id': str(cart.id) if request.user.is_authenticated else 'session',
            'user_id': str(request.user.id) if request.user.is_authenticated else 'guest'
        }

class CartPayPalInitView(BasePaymentInitView):
    gateway_class = PayPalGateway

    def get_amount_and_metadata(self, request, **kwargs):
        cart = CartService.get_or_create_cart(request)
        if request.user.is_authenticated:
            amount = cart.total_price
        else:
            session_cart = request.session.get('cart', {})
            amount = sum(float(i['price']) * i['quantity'] for i in session_cart.values())

        if amount <= 0:
             raise ValueError("Cart is empty or has zero value")

        return amount, {
            'cart_id': str(cart.id) if request.user.is_authenticated else 'session'
        }

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            data = json.loads(payload)
            event_type = data.get('type')

            if event_type == 'payment_intent.succeeded':
                intent = data['data']['object']
                self.handle_successful_payment(intent)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def handle_successful_payment(self, intent):
        metadata = intent.get('metadata', {})
        course_id = metadata.get('course_id')
        user_id = metadata.get('user_id')
        cart_id = metadata.get('cart_id')

        if course_id and user_id:
            self._handle_course_enrollment(course_id, user_id, intent)
        elif cart_id and user_id:
            self._handle_cart_checkout(cart_id, user_id, intent)

    def _handle_course_enrollment(self, course_id, user_id, intent):
        # Project-specific imports removed
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            course = Course.objects.get(id=course_id)
            Enrollment.objects.get_or_create(
                user=user,
                course=course,
                defaults={
                    'payment_status': 'completed',
                    'payment_id': intent.get('id'),
                    'amount_paid': intent.get('amount', 0) / 100,
                    'transaction_date': timezone.now()
                }
            )
            logger.info(f"Webhook enrollment success: {user.email} -> {course.title}")
        except Exception as e:
            logger.error(f"Webhook course enrollment error: {e}")

    def _handle_cart_checkout(self, cart_id, user_id, intent):
        # Implementation for cart checkout success
        logger.info(f"Webhook cart checkout success: Cart {cart_id}, User {user_id}")

class PaymentProcessingMixin:
    """
    Mixin for processing payments in views (like EnrollView).
    """
    def process_stripe_payment(self, request, amount, metadata=None):
        StripeGateway()
        # Mock for now, but centralized
        if amount == 0:
            return {'status': 'success', 'payment_id': 'FREE'}

        # Integration logic would go here
        return {'status': 'success', 'payment_id': f'stripe_processed_{timezone.now().timestamp()}'}

    def process_paypal_payment(self, request, amount, metadata=None):
        PayPalGateway()
        # Mock for now
        return {'status': 'success', 'payment_id': f'paypal_processed_{timezone.now().timestamp()}'}
