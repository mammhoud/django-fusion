"""
Withdrawal model for instructor payout/withdrawal requests.

Instructors can request withdrawals of their earned revenue.
Admins approve and process these requests via the Wagtail snippet admin.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Withdrawal(models.Model):
    """
    Tracks instructor payout / withdrawal requests.

    Status flow:
        pending →  approved → processing → completed
          ↓           ↓
        rejected   cancelled
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        APPROVED = "approved", _("Approved")
        PROCESSING = "processing", _("Processing")
        COMPLETED = "completed", _("Completed")
        REJECTED = "rejected", _("Rejected")
        CANCELLED = "cancelled", _("Cancelled")

    class PaymentMethod(models.TextChoices):
        PAYPAL = "paypal", _("PayPal")
        BANK_TRANSFER = "bank_transfer", _("Bank Transfer")
        STRIPE = "stripe", _("Stripe")

    # Relationships
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="withdrawals",
        verbose_name=_("Instructor"),
    )

    # Financial details
    amount = models.DecimalField(
        _("Amount"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    current_balance = models.DecimalField(
        _("Current Balance"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("Instructor balance at time of request"),
    )

    # Status
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Payment method
    payment_method = models.CharField(
        _("Payment Method"),
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.PAYPAL,
    )

    payment_details = models.JSONField(
        _("Payment Details"),
        default=dict,
        blank=True,
        help_text=_("Payment method-specific details (email, account number, etc.)"),
    )

    # Admin fields
    notes = models.TextField(
        _("Admin Notes"),
        blank=True,
        default="",
        help_text=_("Internal notes about this withdrawal (e.g., rejection reason)"),
    )

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_withdrawals",
        verbose_name=_("Processed By"),
    )

    reference = models.CharField(
        _("Reference"),
        max_length=255,
        blank=True,
        default="",
        help_text=_("Payment processor reference (e.g., PayPal transaction ID)"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    processed_at = models.DateTimeField(
        _("Processed At"),
        null=True,
        blank=True,
        help_text=_("When the withdrawal was completed or rejected"),
    )

    class Meta:
        app_label = "lms"
        db_table = "lms_withdrawals"
        ordering = ["-created_at"]
        verbose_name = _("Withdrawal")
        verbose_name_plural = _("Withdrawals")
        indexes = [
            models.Index(fields=["instructor", "status"]),
            models.Index(fields=["instructor", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.instructor.username} — ${self.amount} ({self.get_status_display()})"

    @property
    def is_pending(self) -> bool:
        return self.status == self.Status.PENDING

    @property
    def is_completed(self) -> bool:
        return self.status == self.Status.COMPLETED

    @property
    def can_cancel(self) -> bool:
        """Instructor can cancel only pending withdrawals."""
        return self.status in (self.Status.PENDING,)

    @property
    def status_display(self) -> str:
        return self.get_status_display()

    def save(self, *args, **kwargs):
        """Auto-set processed_at when status changes to a terminal state."""
        if self.status in (self.Status.COMPLETED, self.Status.REJECTED, self.Status.CANCELLED):
            if not self.processed_at:
                self.processed_at = timezone.now()
        elif self.status not in (self.Status.COMPLETED, self.Status.REJECTED, self.Status.CANCELLED):
            self.processed_at = None
        super().save(*args, **kwargs)
