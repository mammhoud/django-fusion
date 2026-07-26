"""
Data Payments API — Initialize & verify enrollment payments (Pydantic).

Adds the bolt endpoints:
    POST /apis/enrollments/<pk>/payment/init   → PaymentInitResponse
    POST /apis/payments/<tx_id>/verify          → PaymentVerifyResponse
"""

from __future__ import annotations

import json
import logging

from www.api.data.helpers import parse_body, get_current_user
from www.auth import auth_required
from www.schemas import (
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)

logger = logging.getLogger(__name__)


def register_handlers(bolt):
    """Register payment handlers on the given BoltAPI instance."""

    # ── POST /apis/enrollments/<pk>/payment/init — initialize payment ──
    @bolt.post("/enrollments/<int:pk>/payment/init", **auth_required())
    def initialize_payment(request, pk):
        """POST /apis/enrollments/<pk>/payment/init — Init a payment for an enrollment.

        Request body (JSON):
            provider (str):  "stripe", "paypal", or "paymo" (default: "stripe")
            success_url (str): Redirect URL on success
            cancel_url (str):  Redirect URL on cancel

        Response: PaymentInitResponse with payment session details.
        """
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        body = parse_body(request)
        req = PaymentInitRequest(
            provider=body.get("provider", "stripe"),
            success_url=body.get("success_url", ""),
            cancel_url=body.get("cancel_url", ""),
        )

        try:
            from plugins.lms.models import CourseEnrollmentLead

            try:
                enrollment = CourseEnrollmentLead.objects.get(pk=pk)
            except CourseEnrollmentLead.DoesNotExist:
                return {"status": "error", "message": "Enrollment not found"}, 404

            # Verify ownership
            if not user.is_staff and enrollment.email != user.email:
                return {"status": "error", "message": "Permission denied"}, 403

            # Check for active payments
            from plugins.lms.models import PaymentTransaction
            active_payments = PaymentTransaction.objects.filter(
                enrollment=enrollment,
                status__in=["pending", "processing"],
            ).exists()
            if active_payments:
                return {
                    "status": "error",
                    "message": "This enrollment already has an active payment",
                }, 400

            # Get the payment provider
            from plugins.lms.management.services.payment_providers import (
                PaymentProviderRegistry,
                PaymentException,
            )

            try:
                provider = PaymentProviderRegistry.get_provider(req.provider)
            except PaymentException:
                return {"status": "error", "message": f"Invalid provider: {req.provider}"}, 400

            # Initialize payment
            from django.db import transaction

            with transaction.atomic():
                payment_details = provider.initialize_payment(enrollment)

                payment_tx = PaymentTransaction.objects.create(
                    enrollment=enrollment,
                    provider=req.provider,
                    transaction_id=payment_details["transaction_id"],
                    amount=enrollment.course.price if enrollment.course else 0,
                    currency="USD",
                    status="pending",
                    metadata=payment_details,
                )

                logger.info(
                    f"Payment initialized: {payment_tx.id} for enrollment {pk}"
                )

                response = PaymentInitResponse(
                    success=True,
                    transaction_id=payment_tx.id,
                    provider=req.provider,
                    amount=float(payment_tx.amount),
                    currency="USD",
                    redirect_url=payment_details.get("redirect_url"),
                    client_secret=payment_details.get("client_secret"),
                    payment_url=payment_details.get("payment_url"),
                    metadata={k: v for k, v in payment_details.items()
                              if k not in ("redirect_url", "client_secret", "payment_url", "transaction_id")},
                )
                return {"status": "success", "data": response.model_dump()}

        except Exception as exc:
            logger.error(f"Payment init error for enrollment {pk}: {exc}", exc_info=True)
            return {"status": "error", "message": "Payment initialization failed"}, 500

    # ── POST /apis/payments/<tx_id>/verify — verify payment completion ──
    @bolt.post("/payments/<int:tx_id>/verify", **auth_required())
    def verify_payment(request, tx_id):
        """POST /apis/payments/<tx_id>/verify — Verify payment completion.

        Called by the frontend after the user returns from the payment
        provider (Stripe redirect, PayPal approval, Paymo callback).

        Looks up the PaymentTransaction, calls the provider's
        verify_payment() method, updates both the transaction and
        enrollment statuses, and returns the result.

        URL params:
            tx_id (int): PaymentTransaction primary key (Django ID).

        Response: PaymentVerifyResponse
        """
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        try:
            from plugins.lms.models import PaymentTransaction

            try:
                payment_tx = PaymentTransaction.objects.select_related(
                    "enrollment", "enrollment__course"
                ).get(pk=tx_id)
            except PaymentTransaction.DoesNotExist:
                return {"status": "error", "message": "Payment transaction not found"}, 404

            enrollment = payment_tx.enrollment

            # Verify ownership
            if not user.is_staff and enrollment and enrollment.email != user.email:
                return {"status": "error", "message": "Permission denied"}, 403

            # Skip if already processed
            if payment_tx.status in ("completed", "failed", "refunded"):
                return {
                    "status": "success",
                    "data": PaymentVerifyResponse(
                        success=payment_tx.status == "completed",
                        status=payment_tx.status,
                        message=(
                            "Payment already completed"
                            if payment_tx.status == "completed"
                            else "Payment was already processed as failed"
                        ),
                        transaction_id=payment_tx.id,
                        enrollment_id=enrollment.id if enrollment else None,
                        course_title=enrollment.course.name if enrollment and enrollment.course else "",
                        metadata=payment_tx.metadata,
                    ).model_dump(),
                }

            # Get the payment provider
            from plugins.lms.management.services.payment_providers import (
                PaymentProviderRegistry,
                PaymentException,
            )

            try:
                provider = PaymentProviderRegistry.get_provider(payment_tx.provider)
            except PaymentException:
                return {"status": "error", "message": f"Invalid provider: {payment_tx.provider}"}, 500

            from django.db import transaction

            with transaction.atomic():
                try:
                    # Call provider to verify the payment status
                    success, metadata = provider.verify_payment(payment_tx.transaction_id)

                    if success:
                        payment_tx.status = "completed"
                        payment_tx.webhook_verified = True
                        payment_tx.metadata.update(metadata)
                        payment_tx.save()

                        # Update enrollment payment_status
                        if enrollment:
                            enrollment.payment_status = "completed"
                            enrollment.save()

                        logger.info(f"Payment verified & completed: tx {tx_id}, enrollment {enrollment.id if enrollment else '?'}")

                        response = PaymentVerifyResponse(
                            success=True,
                            status="completed",
                            message="Payment confirmed. Welcome to the course!",
                            transaction_id=payment_tx.id,
                            enrollment_id=enrollment.id if enrollment else None,
                            course_title=enrollment.course.name if enrollment and enrollment.course else "",
                            metadata=payment_tx.metadata,
                        )
                        return {"status": "success", "data": response.model_dump()}

                    else:
                        payment_tx.status = "failed"
                        payment_tx.metadata.update(metadata)
                        payment_tx.save()

                        if enrollment:
                            enrollment.payment_status = "failed"
                            enrollment.save()

                        logger.warning(f"Payment verification failed: tx {tx_id}")

                        response = PaymentVerifyResponse(
                            success=False,
                            status="failed",
                            message="Payment verification failed. Please try again.",
                            transaction_id=payment_tx.id,
                            enrollment_id=enrollment.id if enrollment else None,
                            course_title=enrollment.course.name if enrollment and enrollment.course else "",
                            metadata=payment_tx.metadata,
                        )
                        return {"status": "error", "data": response.model_dump()}, 400

                except PaymentException as exc:
                    payment_tx.status = "failed"
                    payment_tx.metadata["error"] = str(exc)
                    payment_tx.save()

                    if enrollment:
                        enrollment.payment_status = "failed"
                        enrollment.save()

                    logger.error(f"Payment verify exception: tx {tx_id}: {exc}", exc_info=True)

                    response = PaymentVerifyResponse(
                        success=False,
                        status="failed",
                        message=str(exc),
                        transaction_id=payment_tx.id,
                        enrollment_id=enrollment.id if enrollment else None,
                        course_title=enrollment.course.name if enrollment and enrollment.course else "",
                        metadata=payment_tx.metadata,
                    )
                    return {"status": "error", "data": response.model_dump()}, 400

        except Exception as exc:
            logger.error(f"Payment verify error for tx {tx_id}: {exc}", exc_info=True)
            return {"status": "error", "message": "Payment verification failed"}, 500
