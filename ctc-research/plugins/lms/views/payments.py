"""
Payment Views for Course Enrollment

Handles payment initialization, verification, and webhook processing.
"""
import hashlib
import hmac
import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from plugins.lms.models import CourseEnrollmentLead, PaymentTransaction
from plugins.lms.management.services.payment_providers import PaymentProviderRegistry, PaymentException
from plugins.lms.forms.enrollment import CourseEnrollmentForm

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def initialize_payment(request, enrollment_id):
    """
    Initialize payment for an enrollment.
    
    Called when user clicks "Pay Now" button.
    Returns payment session details to client.
    """
    try:
        enrollment = get_object_or_404(CourseEnrollmentLead, id=enrollment_id)
        
        # Verify user owns this enrollment (for non-admin users)
        if not request.user.is_staff and enrollment.email != request.user.email:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Check if enrollment already has active payment
        if PaymentTransaction.objects.filter(
            enrollment=enrollment,
            status__in=['pending', 'processing', 'completed']
        ).exists():
            return JsonResponse({
                'error': 'This enrollment already has an active payment'
            }, status=400)
        
        # Get payment provider from request
        provider_name = request.POST.get('provider', 'stripe').lower()
        
        try:
            provider = PaymentProviderRegistry.get_provider(provider_name)
        except PaymentException as e:
            return JsonResponse({'error': str(e)}, status=400)
        
        # Initialize payment with provider
        with transaction.atomic():
            try:
                payment_details = provider.initialize_payment(enrollment)
                
                # Create payment transaction record
                payment_tx = PaymentTransaction.objects.create(
                    enrollment=enrollment,
                    provider=provider_name,
                    transaction_id=payment_details['transaction_id'],
                    amount=enrollment.course.price,
                    currency='USD',
                    status='pending',
                    metadata=payment_details,
                )
                
                logger.info(f"Payment initialized: {payment_tx.id} for enrollment {enrollment_id}")
                
                return JsonResponse({
                    'success': True,
                    'transaction_id': payment_tx.id,
                    **payment_details,
                })
            
            except PaymentException as e:
                logger.error(f"Payment initialization failed: {str(e)}")
                return JsonResponse({'error': str(e)}, status=400)
    
    except CourseEnrollmentLead.DoesNotExist:
        return JsonResponse({'error': 'Enrollment not found'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in initialize_payment: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred'}, status=500)


@login_required
@require_http_methods(["POST"])
def verify_payment(request, transaction_id):
    """
    Verify that payment was completed successfully.
    
    Called after payment processor returns to our site.
    """
    try:
        payment_tx = get_object_or_404(PaymentTransaction, id=transaction_id)
        
        if payment_tx.status in ['completed', 'failed']:
            return JsonResponse({
                'already_processed': True,
                'status': payment_tx.status,
                'message': 'This payment has already been processed'
            }, status=400)
        
        # Get provider and verify payment
        try:
            provider = PaymentProviderRegistry.get_provider(payment_tx.provider)
        except PaymentException as e:
            logger.error(f"Invalid provider: {payment_tx.provider}")
            return JsonResponse({'error': 'Invalid payment provider'}, status=500)
        
        with transaction.atomic():
            try:
                success, metadata = provider.verify_payment(payment_tx.transaction_id)
                
                # Update payment transaction
                if success:
                    payment_tx.status = 'completed'
                    payment_tx.metadata.update(metadata)
                    payment_tx.webhook_verified = True
                    payment_tx.save()
                    
                    # Update enrollment status
                    enrollment = payment_tx.enrollment
                    if enrollment:
                        enrollment.status = 'completed'
                        enrollment.save()
                        
                        # Send confirmation email
                        _send_payment_confirmation_email(enrollment, payment_tx)
                    
                    logger.info(f"Payment verified and completed: {transaction_id}")
                    
                    return JsonResponse({
                        'success': True,
                        'status': 'completed',
                        'message': 'Payment confirmed. Welcome to the course!',
                        'enrollment_id': enrollment.id,
                    })
                else:
                    payment_tx.status = 'failed'
                    payment_tx.metadata.update(metadata)
                    payment_tx.save()
                    
                    logger.warning(f"Payment verification failed: {transaction_id}")
                    
                    return JsonResponse({
                        'success': False,
                        'status': 'failed',
                        'message': 'Payment verification failed',
                    }, status=400)
            
            except PaymentException as e:
                logger.error(f"Payment verification error: {str(e)}")
                payment_tx.status = 'failed'
                payment_tx.metadata['error'] = str(e)
                payment_tx.save()
                
                return JsonResponse({'error': str(e)}, status=400)
    
    except PaymentTransaction.DoesNotExist:
        return JsonResponse({'error': 'Payment transaction not found'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in verify_payment: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred'}, status=500)


@require_http_methods(["GET"])
def payment_status(request, transaction_id):
    """
    Get current payment status.
    
    Can be called by client to poll payment status.
    """
    try:
        payment_tx = get_object_or_404(PaymentTransaction, id=transaction_id)
        
        return JsonResponse({
            'transaction_id': str(payment_tx.id),
            'status': payment_tx.status,
            'provider': payment_tx.provider,
            'amount': str(payment_tx.amount),
            'currency': payment_tx.currency,
            'created_at': payment_tx.created_at.isoformat(),
            'completed_at': payment_tx.completed_at.isoformat() if payment_tx.completed_at else None,
        })
    except PaymentTransaction.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_stripe(request):
    """
    Handle Stripe webhook events.
    
    Webhook URL: /learning/payment/webhook/stripe/
    """
    try:
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
        if webhook_secret:
            import stripe
            try:
                payload = stripe.Webhook.construct_event(
                    request.body, sig_header, webhook_secret
                )
            except (stripe.error.SignatureVerificationError, ValueError):
                logger.warning("Stripe webhook signature verification failed")
                return JsonResponse({"error": "Invalid signature"}, status=400)
        else:
            logger.warning("STRIPE_WEBHOOK_SECRET not configured — skipping signature verification")
            payload = json.loads(request.body)

        # Log webhook
        webhook_log = _log_webhook('stripe', payload)
        
        # Get provider and handle webhook
        provider = PaymentProviderRegistry.get_provider('stripe')
        result = provider.handle_webhook(payload)
        
        # Process webhook result
        if result.get('processed'):
            with transaction.atomic():
                # Find or create payment transaction
                payment_tx = PaymentTransaction.objects.filter(
                    transaction_id=result.get('transaction_id'),
                    provider='stripe'
                ).first()
                
                if payment_tx:
                    payment_tx.status = result.get('status', 'pending')
                    payment_tx.webhook_verified = True
                    payment_tx.save()
                    
                    webhook_log.transaction = payment_tx
                    webhook_log.processed = True
                    webhook_log.save()
                    
                    logger.info(f"Stripe webhook processed: {result.get('transaction_id')}")
        
        return JsonResponse({'status': 'received'}, status=200)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Stripe webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Webhook processing failed'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_paypal(request):
    """
    Handle PayPal webhook events.
    
    Webhook URL: /learning/payment/webhook/paypal/
    """
    try:
        webhook_id = getattr(settings, "PAYPAL_WEBHOOK_ID", "")
        if webhook_id:
            transmission_id = request.META.get("HTTP_PAYPAL_TRANSMISSION_ID", "")
            timestamp = request.META.get("HTTP_PAYPAL_TRANSMISSION_TIME", "")
            actual_sig = request.META.get("HTTP_PAYPAL_TRANSMISSION_SIG", "")
            if not (transmission_id and timestamp and actual_sig):
                logger.warning("PayPal webhook missing signature headers")
                return JsonResponse({"error": "Missing signature headers"}, status=400)
        else:
            logger.warning("PAYPAL_WEBHOOK_ID not configured — skipping signature verification")

        payload = json.loads(request.body)
        
        # Log webhook
        webhook_log = _log_webhook('paypal', payload)
        
        # Get provider and handle webhook
        provider = PaymentProviderRegistry.get_provider('paypal')
        result = provider.handle_webhook(payload)
        
        # Process webhook result
        if result.get('processed'):
            with transaction.atomic():
                # Find or create payment transaction
                payment_tx = PaymentTransaction.objects.filter(
                    transaction_id=result.get('transaction_id'),
                    provider='paypal'
                ).first()
                
                if payment_tx:
                    payment_tx.status = result.get('status', 'pending')
                    payment_tx.webhook_verified = True
                    payment_tx.save()
                    
                    webhook_log.transaction = payment_tx
                    webhook_log.processed = True
                    webhook_log.save()
                    
                    logger.info(f"PayPal webhook processed: {result.get('transaction_id')}")
        
        return JsonResponse({'status': 'received'}, status=200)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in PayPal webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing PayPal webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Webhook processing failed'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_paymo(request):
    """
    Handle Paymo webhook events.
    
    Webhook URL: /learning/payment/webhook/paymo/
    """
    try:
        webhook_secret = getattr(settings, "PAYMO_WEBHOOK_SECRET", "")
        if webhook_secret:
            sig_header = request.META.get("HTTP_X_PAYMO_SIGNATURE", "")
            expected_sig = hmac.new(
                webhook_secret.encode(), request.body, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(sig_header, expected_sig):
                logger.warning("Paymo webhook signature verification failed")
                return JsonResponse({"error": "Invalid signature"}, status=400)
        else:
            logger.warning("PAYMO_WEBHOOK_SECRET not configured — skipping signature verification")

        payload = json.loads(request.body)
        
        # Log webhook
        webhook_log = _log_webhook('paymo', payload)
        
        # Get provider and handle webhook
        provider = PaymentProviderRegistry.get_provider('paymo')
        result = provider.handle_webhook(payload)
        
        # Process webhook result
        if result.get('processed'):
            with transaction.atomic():
                # Find or create payment transaction
                payment_tx = PaymentTransaction.objects.filter(
                    transaction_id=result.get('transaction_id'),
                    provider='paymo'
                ).first()
                
                if payment_tx:
                    payment_tx.status = result.get('status', 'pending')
                    payment_tx.webhook_verified = True
                    payment_tx.save()
                    
                    webhook_log.transaction = payment_tx
                    webhook_log.processed = True
                    webhook_log.save()
                    
                    logger.info(f"Paymo webhook processed: {result.get('transaction_id')}")
        
        return JsonResponse({'status': 'received'}, status=200)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Paymo webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing Paymo webhook: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Webhook processing failed'}, status=500)


def _log_webhook(provider, payload):
    """Log webhook event"""
    from plugins.lms.models import PaymentWebhookLog
    
    event_type = payload.get('event_type') or payload.get('type', 'unknown')
    
    webhook_log = PaymentWebhookLog.objects.create(
        provider=provider,
        event_id=payload.get('id', ''),
        event_type=event_type,
        payload=payload,
        verified=False,
    )
    return webhook_log


def _send_payment_confirmation_email(enrollment, payment_tx):
    """
    Send payment confirmation email to enrollee.
    """
    try:
        context = {
            'enrollment': enrollment,
            'payment': payment_tx,
            'course': enrollment.course,
            'site_url': settings.BASE_URL,
        }
        
        # Send HTML email
        html_message = render_to_string('lms/emails/payment_confirmation.html', context)
        send_mail(
            subject=f"Payment Confirmed - {enrollment.course.name}",
            message=render_to_string('lms/emails/payment_confirmation.txt', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[enrollment.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Payment confirmation email sent to {enrollment.email}")
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email: {str(e)}")
