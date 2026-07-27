"""
Payment Models for CTC Research LMS

Tracks payment provider integrations, transactions, and status
for course enrollment and purchases.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class PaymentTransaction(models.Model):
    """
    Tracks payment transactions across all providers.
    One transaction per enrollment attempt.
    """
    
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('paymo', 'Paymo'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Relationships
    enrollment = models.OneToOneField(
        'CourseEnrollmentLead',
        on_delete=models.CASCADE,
        related_name='payment_transaction',
        null=True,
        blank=True,
        help_text='Associated enrollment lead'
    )
    
    # Provider Information
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        help_text='Payment provider used'
    )
    transaction_id = models.CharField(
        max_length=255,
        unique=True,
        help_text='Provider transaction ID'
    )
    
    # Payment Details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Amount in provider currency'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text='ISO 4217 currency code'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current payment status'
    )
    
    # Payment Method
    payment_method = models.CharField(
        max_length=100,
        blank=True,
        help_text='Card, PayPal account, etc.'
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Provider-specific data'
    )
    
    # Webhook
    webhook_verified = models.BooleanField(
        default=False,
        help_text='Whether webhook from provider was verified'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When payment completed successfully'
    )
    
    class Meta:
        app_label = "lms"
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.provider.upper()} - {self.transaction_id} ({self.status})"
    
    @property
    def is_success(self):
        """Check if payment was successful"""
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        """Check if payment failed"""
        return self.status in ['failed', 'cancelled']
    
    @property
    def can_retry(self):
        """Check if payment can be retried"""
        return self.status in ['failed', 'pending']


class PaymentRefund(models.Model):
    """
    Track refunds for completed payments.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.CASCADE,
        related_name='refunds',
        help_text='Original payment transaction'
    )
    
    refund_id = models.CharField(
        max_length=255,
        unique=True,
        help_text='Provider refund ID'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Refund amount'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Refund status'
    )
    
    reason = models.CharField(
        max_length=200,
        blank=True,
        help_text='Reason for refund'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Provider-specific data'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When refund completed'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Refund'
        verbose_name_plural = 'Payment Refunds'
    
    def __str__(self):
        return f"Refund {self.refund_id} - {self.amount} {self.transaction.currency}"


class PaymentWebhookLog(models.Model):
    """
    Log all webhook events from payment providers.
    Useful for debugging and audit trails.
    """
    
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('paymo', 'Paymo'),
    ]
    
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        help_text='Provider sending webhook'
    )
    
    event_id = models.CharField(
        max_length=255,
        help_text='Provider event ID'
    )
    
    event_type = models.CharField(
        max_length=100,
        help_text='Event type (e.g., payment.success, payment.failed)'
    )
    
    payload = models.JSONField(
        help_text='Full webhook payload'
    )
    
    verified = models.BooleanField(
        default=False,
        help_text='Whether webhook signature was verified'
    )
    
    processed = models.BooleanField(
        default=False,
        help_text='Whether webhook was processed'
    )
    
    transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='webhook_logs',
        help_text='Associated transaction if found'
    )
    
    error_message = models.TextField(
        blank=True,
        help_text='Error message if processing failed'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When webhook was processed'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Webhook Log'
        verbose_name_plural = 'Payment Webhook Logs'
        indexes = [
            models.Index(fields=['provider', 'event_type']),
            models.Index(fields=['verified', 'processed']),
        ]
    
    def __str__(self):
        return f"{self.provider.upper()} - {self.event_type} ({self.event_id})"
