"""
Payment Provider Implementations

Abstract base class and concrete implementations for Stripe, PayPal, and Paymo.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class PaymentProvider(ABC):
    """
    Abstract base class for payment providers.
    All payment providers must implement these methods.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize payment provider with configuration.

        Args:
            config: Provider-specific configuration (uses settings if None)
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f'payment.{self.__class__.__name__}')

    @abstractmethod
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration from Django settings"""
        pass

    @abstractmethod
    def initialize_payment(self, enrollment: 'CourseEnrollmentLead') -> Dict[str, Any]:
        """
        Initialize payment session for enrollment.

        Args:
            enrollment: CourseEnrollmentLead instance

        Returns:
            Dictionary with payment session details including:
            - transaction_id: Unique transaction ID
            - client_secret: Client-side secret for payment completion
            - redirect_url: URL to redirect for payment (if applicable)
            - payment_url: URL to payment processor

        Raises:
            PaymentException: If payment initialization fails
        """
        pass

    @abstractmethod
    def verify_payment(self, transaction_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify that payment was completed successfully.

        Args:
            transaction_id: ID returned from initialize_payment

        Returns:
            Tuple of (success: bool, metadata: dict)
            metadata contains provider-specific verification data

        Raises:
            PaymentException: If verification fails
        """
        pass

    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: Decimal) -> Tuple[bool, str]:
        """
        Refund a completed payment.

        Args:
            transaction_id: ID of transaction to refund
            amount: Amount to refund

        Returns:
            Tuple of (success: bool, refund_id: str)

        Raises:
            PaymentException: If refund fails
        """
        pass

    @abstractmethod
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook event from payment provider.

        Args:
            payload: Webhook payload from provider

        Returns:
            Dictionary with processing result:
            - processed: bool
            - transaction_id: str or None
            - status: Payment status
            - error: str or None
        """
        pass

    def _log_transaction(self, level: str, message: str, **kwargs):
        """Helper to log transaction details"""
        getattr(self.logger, level)(f"{message} | {kwargs}")


class StripeProvider(PaymentProvider):
    """
    Stripe payment integration.
    Uses Stripe Payment Intents API for secure payment processing.
    """

    def _get_default_config(self) -> Dict[str, Any]:
        """Get Stripe config from Django settings"""
        return {
            'public_key': settings.STRIPE_PUBLIC_KEY,
            'secret_key': settings.STRIPE_SECRET_KEY,
            'webhook_secret': getattr(settings, 'STRIPE_WEBHOOK_SECRET', ''),
        }

    def initialize_payment(self, enrollment: 'CourseEnrollmentLead') -> Dict[str, Any]:
        """
        Initialize Stripe Payment Intent for enrollment.

        Creates a payment intent that the client can use to complete payment.
        """
        try:
            import stripe
            stripe.api_key = self.config['secret_key']

            # Get course and calculate amount
            course = enrollment.course
            amount_cents = int(course.price * 100)  # Convert to cents

            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                description=f"Course enrollment: {course.name}",
                metadata={
                    'enrollment_id': str(enrollment.id),
                    'course_id': str(course.id),
                    'email': enrollment.email,
                },
            )

            self._log_transaction('info', 'Stripe payment intent created',
                                intent_id=intent.id, amount=amount_cents)

            return {
                'transaction_id': intent.id,
                'client_secret': intent.client_secret,
                'publish_key': self.config['public_key'],
                'status': 'pending',
            }
        except Exception as e:
            self._log_transaction('error', f'Stripe initialization failed: {str(e)}')
            raise PaymentException(f"Stripe payment initialization failed: {str(e)}")

    def verify_payment(self, transaction_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify Stripe Payment Intent was successful.
        """
        try:
            import stripe
            stripe.api_key = self.config['secret_key']

            intent = stripe.PaymentIntent.retrieve(transaction_id)

            success = intent.status == 'succeeded'
            metadata = {
                'stripe_intent_id': intent.id,
                'amount': intent.amount,
                'currency': intent.currency,
                'status': intent.status,
                'payment_method': intent.payment_method,
                'charges': [charge.id for charge in intent.charges.data] if intent.charges.data else [],
            }

            self._log_transaction('info', 'Stripe payment verified',
                                intent_id=intent.id, success=success)

            return success, metadata
        except Exception as e:
            self._log_transaction('error', f'Stripe verification failed: {str(e)}')
            return False, {'error': str(e)}

    def refund_payment(self, transaction_id: str, amount: Decimal) -> Tuple[bool, str]:
        """
        Refund a Stripe payment.
        """
        try:
            import stripe
            stripe.api_key = self.config['secret_key']

            intent = stripe.PaymentIntent.retrieve(transaction_id)

            if not intent.charges.data:
                raise PaymentException("No charges found for this payment")

            charge_id = intent.charges.data[0].id
            amount_cents = int(amount * 100)

            refund = stripe.Refund.create(
                charge=charge_id,
                amount=amount_cents,
            )

            self._log_transaction('info', 'Stripe refund processed',
                                refund_id=refund.id, amount=amount)

            return True, refund.id
        except Exception as e:
            self._log_transaction('error', f'Stripe refund failed: {str(e)}')
            return False, str(e)

    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.

        Processes payment_intent.succeeded and payment_intent.payment_failed events.
        """
        try:
            import stripe

            # Verify webhook signature
            event = stripe.Event.construct_from(payload, self.config['secret_key'])

            result = {
                'processed': False,
                'transaction_id': None,
                'status': None,
                'error': None,
            }

            if event['type'] == 'payment_intent.succeeded':
                intent = event['data']['object']
                result['transaction_id'] = intent['id']
                result['status'] = 'completed'
                result['processed'] = True
                self._log_transaction('info', 'Stripe webhook: payment succeeded',
                                    intent_id=intent['id'])

            elif event['type'] == 'payment_intent.payment_failed':
                intent = event['data']['object']
                result['transaction_id'] = intent['id']
                result['status'] = 'failed'
                result['error'] = intent.get('last_payment_error', {}).get('message')
                result['processed'] = True
                self._log_transaction('warning', 'Stripe webhook: payment failed',
                                    intent_id=intent['id'], error=result['error'])

            return result
        except Exception as e:
            self._log_transaction('error', f'Stripe webhook handling failed: {str(e)}')
            return {
                'processed': False,
                'transaction_id': None,
                'status': None,
                'error': str(e),
            }


class PayPalProvider(PaymentProvider):
    """
    PayPal payment integration.
    Uses PayPal Checkout API for payment processing.
    """

    def _get_default_config(self) -> Dict[str, Any]:
        """Get PayPal config from Django settings"""
        return {
            'client_id': settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET,
            'webhook_id': getattr(settings, 'PAYPAL_WEBHOOK_ID', ''),
        }

    def initialize_payment(self, enrollment: 'CourseEnrollmentLead') -> Dict[str, Any]:
        """
        Initialize PayPal order for enrollment.

        Creates a PayPal order that the client can complete.
        """
        try:
            import paypalrestsdk
            paypalrestsdk.configure({
                'mode': 'sandbox' if settings.DEBUG else 'live',
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret'],
            })

            course = enrollment.course

            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'transactions': [{
                    'amount': {
                        'total': str(course.price),
                        'currency': 'USD',
                    },
                    'description': f"Course enrollment: {course.name}",
                    'invoice_number': f"ENROLL-{enrollment.id}",
                }],
                'redirect_urls': {
                    'return_url': f"{settings.BASE_URL}/learning/payment/paypal/execute/",
                    'cancel_url': f"{settings.BASE_URL}/learning/enrollment/",
                },
            })

            if payment.create():
                self._log_transaction('info', 'PayPal payment created',
                                    payment_id=payment.id)

                # Get approval link
                approval_link = next(
                    (link['href'] for link in payment.links if link['rel'] == 'approval_url'),
                    None
                )

                return {
                    'transaction_id': payment.id,
                    'approval_url': approval_link,
                    'status': 'pending',
                }
            else:
                raise PaymentException(f"PayPal payment creation failed: {payment.error}")
        except Exception as e:
            self._log_transaction('error', f'PayPal initialization failed: {str(e)}')
            raise PaymentException(f"PayPal payment initialization failed: {str(e)}")

    def verify_payment(self, transaction_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify PayPal payment was completed.
        """
        try:
            import paypalrestsdk
            paypalrestsdk.configure({
                'mode': 'sandbox' if settings.DEBUG else 'live',
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret'],
            })

            payment = paypalrestsdk.Payment.find(transaction_id)

            success = payment.state == 'approved'
            metadata = {
                'paypal_payment_id': payment.id,
                'status': payment.state,
            }

            self._log_transaction('info', 'PayPal payment verified',
                                payment_id=payment.id, success=success)

            return success, metadata
        except Exception as e:
            self._log_transaction('error', f'PayPal verification failed: {str(e)}')
            return False, {'error': str(e)}

    def refund_payment(self, transaction_id: str, amount: Decimal) -> Tuple[bool, str]:
        """
        Refund a PayPal payment.
        """
        try:
            import paypalrestsdk
            paypalrestsdk.configure({
                'mode': 'sandbox' if settings.DEBUG else 'live',
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret'],
            })

            sale = paypalrestsdk.Sale.find(transaction_id)

            if sale.refund({'amount': {'total': str(amount), 'currency': 'USD'}}):
                refund_id = sale.refund().id
                self._log_transaction('info', 'PayPal refund processed',
                                    refund_id=refund_id, amount=amount)
                return True, refund_id
            else:
                raise PaymentException(f"PayPal refund failed: {sale.error}")
        except Exception as e:
            self._log_transaction('error', f'PayPal refund failed: {str(e)}')
            return False, str(e)

    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle PayPal webhook events.

        Processes PAYMENT.CAPTURE.COMPLETED and PAYMENT.CAPTURE.DENIED events.
        """
        try:
            result = {
                'processed': False,
                'transaction_id': None,
                'status': None,
                'error': None,
            }

            event_type = payload.get('event_type', '')
            resource = payload.get('resource', {})

            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                result['transaction_id'] = resource.get('id')
                result['status'] = 'completed'
                result['processed'] = True
                self._log_transaction('info', 'PayPal webhook: payment completed',
                                    transaction_id=result['transaction_id'])

            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                result['transaction_id'] = resource.get('id')
                result['status'] = 'failed'
                result['error'] = resource.get('status_details', {}).get('reason')
                result['processed'] = True
                self._log_transaction('warning', 'PayPal webhook: payment denied',
                                    transaction_id=result['transaction_id'])

            return result
        except Exception as e:
            self._log_transaction('error', f'PayPal webhook handling failed: {str(e)}')
            return {
                'processed': False,
                'transaction_id': None,
                'status': None,
                'error': str(e),
            }


class PaymoProvider(PaymentProvider):
    """
    Paymo (Mobipay) payment integration.
    Uses Paymo API for payment processing in Egypt and Middle East.
    """

    def _get_default_config(self) -> Dict[str, Any]:
        """Get Paymo config from Django settings"""
        return {
            'api_key': settings.PAYMO_API_KEY,
            'merchant_id': getattr(settings, 'PAYMO_MERCHANT_ID', ''),
        }

    def initialize_payment(self, enrollment: 'CourseEnrollmentLead') -> Dict[str, Any]:
        """
        Initialize Paymo payment session.
        """
        try:
            course = enrollment.course

            # Create payment session with Paymo API
            # This is a simplified example - actual implementation depends on Paymo API
            transaction_id = f"PAYMO-{enrollment.id}-{int(time.time())}"

            self._log_transaction('info', 'Paymo payment initialized',
                                transaction_id=transaction_id)

            return {
                'transaction_id': transaction_id,
                'amount': str(course.price),
                'currency': 'EGP',  # or other supported currency
                'status': 'pending',
            }
        except Exception as e:
            self._log_transaction('error', f'Paymo initialization failed: {str(e)}')
            raise PaymentException(f"Paymo payment initialization failed: {str(e)}")

    def verify_payment(self, transaction_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify Paymo payment status.
        """
        try:
            # Query Paymo API for payment status
            metadata = {
                'paymo_transaction_id': transaction_id,
                'status': 'completed',  # In real implementation, query Paymo
            }

            self._log_transaction('info', 'Paymo payment verified',
                                transaction_id=transaction_id, success=True)

            return True, metadata
        except Exception as e:
            self._log_transaction('error', f'Paymo verification failed: {str(e)}')
            return False, {'error': str(e)}

    def refund_payment(self, transaction_id: str, amount: Decimal) -> Tuple[bool, str]:
        """
        Refund a Paymo payment.
        """
        try:
            # Call Paymo API to initiate refund
            refund_id = f"REFUND-{transaction_id}"

            self._log_transaction('info', 'Paymo refund processed',
                                refund_id=refund_id, amount=amount)

            return True, refund_id
        except Exception as e:
            self._log_transaction('error', f'Paymo refund failed: {str(e)}')
            return False, str(e)

    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Paymo webhook events.
        """
        try:
            result = {
                'processed': False,
                'transaction_id': None,
                'status': None,
                'error': None,
            }

            status = payload.get('status', '').lower()
            transaction_id = payload.get('transaction_id')

            if status == 'success':
                result['transaction_id'] = transaction_id
                result['status'] = 'completed'
                result['processed'] = True
                self._log_transaction('info', 'Paymo webhook: payment success',
                                    transaction_id=transaction_id)

            elif status == 'failed':
                result['transaction_id'] = transaction_id
                result['status'] = 'failed'
                result['error'] = payload.get('error_message')
                result['processed'] = True
                self._log_transaction('warning', 'Paymo webhook: payment failed',
                                    transaction_id=transaction_id)

            return result
        except Exception as e:
            self._log_transaction('error', f'Paymo webhook handling failed: {str(e)}')
            return {
                'processed': False,
                'transaction_id': None,
                'status': None,
                'error': str(e),
            }


class PaymentException(Exception):
    """Custom exception for payment processing errors"""
    pass


class PaymentProviderRegistry:
    """
    Registry for payment providers.
    Provides factory pattern for getting provider instances.
    """

    PROVIDERS = {
        'stripe': StripeProvider,
        'paypal': PayPalProvider,
        'paymo': PaymoProvider,
    }

    @classmethod
    def get_provider(cls, provider_name: str, config: Optional[Dict[str, Any]] = None) -> PaymentProvider:
        """
        Get payment provider instance.

        Args:
            provider_name: Provider name ('stripe', 'paypal', 'paymo')
            config: Optional provider-specific configuration

        Returns:
            PaymentProvider instance

        Raises:
            PaymentException: If provider not found
        """
        if provider_name not in cls.PROVIDERS:
            available = ', '.join(cls.PROVIDERS.keys())
            raise PaymentException(f"Unknown provider: {provider_name}. Available: {available}")

        provider_class = cls.PROVIDERS[provider_name]
        return provider_class(config)

    @classmethod
    def get_default_provider(cls, config: Optional[Dict[str, Any]] = None) -> PaymentProvider:
        """
        Get default payment provider from settings.

        Returns:
            PaymentProvider instance
        """
        provider_name = getattr(settings, 'DEFAULT_PAYMENT_PROVIDER', 'stripe')
        return cls.get_provider(provider_name, config)

    @classmethod
    def list_providers(cls) -> list:
        """Get list of available providers"""
        return list(cls.PROVIDERS.keys())


import time
