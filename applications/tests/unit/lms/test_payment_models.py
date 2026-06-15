"""
Unit tests for LMS payment models.
"""
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from ctc_research.plugins.lms.models import (
    Course,
    CourseEnrollmentLead,
    PaymentTransaction,
    PaymentRefund,
    PaymentWebhookLog,
)

User = get_user_model()


class TestPaymentTransaction:
    """Test PaymentTransaction model."""

    def test_create_payment_transaction(self, db, user, course, enrollment_lead):
        """Test creating a payment transaction."""
        transaction = PaymentTransaction.objects.create(
            enrollment=enrollment_lead,
            user=user,
            amount=Decimal("99.99"),
            currency="USD",
            provider="stripe",
            status="completed",
            transaction_id="txn_12345"
        )
        assert transaction.enrollment == enrollment_lead
        assert transaction.user == user
        assert transaction.amount == Decimal("99.99")
        assert transaction.provider == "stripe"
        assert transaction.status == "completed"

    def test_payment_transaction_status_choices(self, db, user, enrollment_lead):
        """Test payment transaction status choices."""
        statuses = ["pending", "processing", "completed", "failed", "refunded"]
        for status in statuses:
            transaction = PaymentTransaction.objects.create(
                enrollment=enrollment_lead,
                user=user,
                amount=Decimal("99.99"),
                currency="USD",
                provider="stripe",
                status=status,
                transaction_id=f"txn_{status}"
            )
            assert transaction.status == status

    def test_payment_provider_choices(self, db, user, enrollment_lead):
        """Test payment provider choices."""
        providers = ["stripe", "paypal", "paymo"]
        for provider in providers:
            transaction = PaymentTransaction.objects.create(
                enrollment=enrollment_lead,
                user=user,
                amount=Decimal("99.99"),
                currency="USD",
                provider=provider,
                status="completed",
                transaction_id=f"txn_{provider}"
            )
            assert transaction.provider == provider

    def test_payment_transaction_amount(self, db, user, enrollment_lead):
        """Test payment transaction amount handling."""
        transaction = PaymentTransaction.objects.create(
            enrollment=enrollment_lead,
            user=user,
            amount=Decimal("123.45"),
            currency="USD",
            provider="stripe",
            status="completed",
            transaction_id="txn_123"
        )
        assert transaction.amount == Decimal("123.45")
        assert isinstance(transaction.amount, Decimal)

    def test_payment_transaction_timestamps(self, db, user, enrollment_lead):
        """Test payment transaction timestamps."""
        transaction = PaymentTransaction.objects.create(
            enrollment=enrollment_lead,
            user=user,
            amount=Decimal("99.99"),
            currency="USD",
            provider="stripe",
            status="completed",
            transaction_id="txn_123"
        )
        assert transaction.created_at is not None
        assert transaction.updated_at is not None

    def test_payment_transaction_string_representation(self, db, user, enrollment_lead):
        """Test payment transaction string representation."""
        transaction = PaymentTransaction.objects.create(
            enrollment=enrollment_lead,
            user=user,
            amount=Decimal("99.99"),
            currency="USD",
            provider="stripe",
            status="completed",
            transaction_id="txn_123"
        )
        # Should include relevant information
        assert "stripe" in str(transaction).lower() or "txn" in str(transaction)


class TestPaymentRefund:
    """Test PaymentRefund model."""

    def test_create_refund(self, db, user, enrollment_lead):
        """Test creating a payment refund."""
        transaction = PaymentTransaction.objects.create(
            enrollment=enrollment_lead,
            user=user,
            amount=Decimal("99.99"),
            currency="USD",
            provider="stripe",
            status="completed",
            transaction_id="txn_123"
        )
        
        refund = PaymentRefund.objects.create(
            transaction=transaction,
            amount=Decimal("99.99"),
            reason="customer_request",
            status="completed",
            refund_id="ref_123"
        )
        
        assert refund.transaction == transaction
        assert refund.amount == Decimal("99.99")
        assert refund.status == "completed"

    def test_refund_reason_choices(self, db, user, enrollment_lead):
        """Test refund reason choices."""
        transaction = PaymentTransaction.objects.create(
            enrollment=enrollment_lead,
            user=user,
            amount=Decimal("99.99"),
            currency="USD",
            provider="stripe",
            status="completed",
            transaction_id="txn_123"
        )
        
        reasons = [
            "customer_request",
            "duplicate",
            "fraudulent",
            "unspecified"
        ]
        
        for i, reason in enumerate(reasons):
            refund = PaymentRefund.objects.create(
                transaction=transaction,
                amount=Decimal("10.00"),
                reason=reason,
                status="completed",
                refund_id=f"ref_{i}"
            )
            assert refund.reason == reason

    def test_refund_status_choices(self, db, user, enrollment_lead):
        """Test refund status choices."""
        transaction = PaymentTransaction.objects.create(
            enrollment=enrollment_lead,
            user=user,
            amount=Decimal("99.99"),
            currency="USD",
            provider="stripe",
            status="completed",
            transaction_id="txn_123"
        )
        
        statuses = ["pending", "processing", "completed", "failed"]
        
        for status in statuses:
            refund = PaymentRefund.objects.create(
                transaction=transaction,
                amount=Decimal("10.00"),
                reason="customer_request",
                status=status,
                refund_id=f"ref_{status}"
            )
            assert refund.status == status

    def test_refund_partial_amount(self, db, user, enrollment_lead):
        """Test partial refunds."""
        transaction = PaymentTransaction.objects.create(
            enrollment=enrollment_lead,
            user=user,
            amount=Decimal("100.00"),
            currency="USD",
            provider="stripe",
            status="completed",
            transaction_id="txn_123"
        )
        
        # Partial refund
        refund = PaymentRefund.objects.create(
            transaction=transaction,
            amount=Decimal("50.00"),  # Partial
            reason="customer_request",
            status="completed",
            refund_id="ref_partial"
        )
        
        assert refund.amount == Decimal("50.00")
        assert refund.amount < transaction.amount


class TestPaymentWebhookLog:
    """Test PaymentWebhookLog model."""

    def test_create_webhook_log(self, db):
        """Test creating a webhook log."""
        webhook_log = PaymentWebhookLog.objects.create(
            provider="stripe",
            event_type="charge.completed",
            payload={"id": "evt_123", "data": {}},
            status="processed",
            webhook_id="whk_123"
        )
        
        assert webhook_log.provider == "stripe"
        assert webhook_log.event_type == "charge.completed"
        assert webhook_log.status == "processed"

    def test_webhook_status_choices(self, db):
        """Test webhook status choices."""
        statuses = ["received", "processing", "processed", "failed"]
        
        for status in statuses:
            webhook = PaymentWebhookLog.objects.create(
                provider="stripe",
                event_type="charge.completed",
                payload={},
                status=status,
                webhook_id=f"whk_{status}"
            )
            assert webhook.status == status

    def test_webhook_payload_storage(self, db):
        """Test webhook payload storage."""
        payload = {
            "id": "evt_123",
            "type": "charge.completed",
            "data": {
                "object": {
                    "id": "ch_123",
                    "amount": 9999,
                    "currency": "usd"
                }
            }
        }
        
        webhook = PaymentWebhookLog.objects.create(
            provider="stripe",
            event_type="charge.completed",
            payload=payload,
            status="processed",
            webhook_id="whk_123"
        )
        
        assert webhook.payload == payload
        assert webhook.payload["data"]["object"]["amount"] == 9999

    def test_webhook_timestamps(self, db):
        """Test webhook log timestamps."""
        webhook = PaymentWebhookLog.objects.create(
            provider="stripe",
            event_type="charge.completed",
            payload={},
            status="processed",
            webhook_id="whk_123"
        )
        
        assert webhook.created_at is not None
        assert webhook.processed_at is None  # May be None until actually processed
        
        # Simulate processing
        webhook.processed_at = timezone.now()
        webhook.save()
        assert webhook.processed_at is not None

    def test_multiple_webhooks(self, db):
        """Test storing multiple webhooks."""
        for i in range(5):
            PaymentWebhookLog.objects.create(
                provider="stripe",
                event_type="charge.completed",
                payload={"event": i},
                status="processed",
                webhook_id=f"whk_{i}"
            )
        
        webhooks = PaymentWebhookLog.objects.all()
        assert webhooks.count() == 5


class TestPaymentWorkflow:
    """Test payment workflow and transaction tracking."""

    def test_complete_payment_workflow(self, db, user, enrollment_lead):
        """Test a complete payment workflow."""
        # 1. Create transaction (payment initiated)
        transaction = PaymentTransaction.objects.create(
            enrollment=enrollment_lead,
            user=user,
            amount=Decimal("99.99"),
            currency="USD",
            provider="stripe",
            status="processing",
            transaction_id="txn_123"
        )
        assert transaction.status == "processing"
        
        # 2. Webhook received
        webhook = PaymentWebhookLog.objects.create(
            provider="stripe",
            event_type="charge.completed",
            payload={"charge": "ch_123"},
            status="processed",
            webhook_id="whk_123"
        )
        assert webhook.status == "processed"
        
        # 3. Transaction completed
        transaction.status = "completed"
        transaction.save()
        assert transaction.status == "completed"
        
        # 4. Later: Customer requests refund
        refund = PaymentRefund.objects.create(
            transaction=transaction,
            amount=Decimal("99.99"),
            reason="customer_request",
            status="completed",
            refund_id="ref_123"
        )
        assert refund.status == "completed"

    def test_failed_payment(self, db, user, enrollment_lead):
        """Test a failed payment scenario."""
        transaction = PaymentTransaction.objects.create(
            enrollment=enrollment_lead,
            user=user,
            amount=Decimal("99.99"),
            currency="USD",
            provider="stripe",
            status="processing",
            transaction_id="txn_failed"
        )
        
        # Simulate failure
        transaction.status = "failed"
        transaction.save()
        
        assert transaction.status == "failed"
        
        # No refund for failed payment
        refunds = PaymentRefund.objects.filter(transaction=transaction)
        assert refunds.count() == 0
