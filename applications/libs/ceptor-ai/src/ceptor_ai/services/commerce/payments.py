"""
Payment gateway services.

Canonical imports::
    from ceptor_ai.services import PaymentGateway
    from ceptor_ai.services import StripeGateway
    from ceptor_ai.services import PayPalGateway
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)

class PaymentGateway:
    """
    Base class for payment gateways.
    """
    def initialize_payment(self, amount, currency="usd", metadata=None):
        raise NotImplementedError("Subclasses must implement initialize_payment")

    def capture_payment(self, payment_id):
        raise NotImplementedError("Subclasses must implement capture_payment")


class StripeGateway(PaymentGateway):
    def __init__(self):
        import stripe
        self._stripe = stripe
        self.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)
        if self.api_key:
            self._stripe.api_key = self.api_key

    def initialize_payment(self, amount, currency="usd", metadata=None):
        """
        Create a Stripe PaymentIntent.
        """
        if not self.api_key:
            logger.warning("Stripe API key is missing. Using mock initialization.")
            return {
                "client_secret": "mock_stripe_secret",
                "payment_id": "mock_stripe_id"
            }

        try:
            intent = self._stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe uses cents
                currency=currency,
                metadata=metadata or {},
                payment_method_types=["card"],
            )
            return {
                "client_secret": intent.client_secret,
                "payment_id": intent.id
            }
        except Exception as e:
            logger.error(f"Stripe initialization failed: {e}")
            return None


class PayPalGateway(PaymentGateway):
    def __init__(self):
        self.client_id = getattr(settings, "PAYPAL_CLIENT_ID", None)
        self.client_secret = getattr(settings, "PAYPAL_CLIENT_SECRET", None)

    def initialize_payment(self, amount, currency="usd", metadata=None):
        """
        Mock PayPal order creation. In production, use paypal-checkout-sdk.
        """
        if not self.client_id:
            logger.warning("PayPal Client ID is missing. Using mock initialization.")

        return {
            "order_id": "mock_paypal_order_id",
            "approval_url": f"https://www.paypal.com/checkoutnow?token=mock_order_id"
        }

    def capture_payment(self, order_id):
        """
        Capture a PayPal order.
        """
        # Actual implementation would call PayPal API to capture
        return {"status": "COMPLETED", "id": order_id}
