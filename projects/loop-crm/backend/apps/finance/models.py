"""Loop-CRM finance module.

Finance is intentionally connected to the CRM graph instead of becoming a
second sales ledger: invoices and revenue events can point at a deal, company,
contact, and campaign, while payment state remains auditable and tenant-safe.
"""
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import Workspace


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("issued", "Issued"),
        ("partially_paid", "Partially paid"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("void", "Void"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="invoices")
    number = models.CharField(max_length=40)
    company = models.ForeignKey("crm.Company", on_delete=models.PROTECT, related_name="invoices")
    contact = models.ForeignKey("crm.Contact", on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")
    deal = models.ForeignKey("crm.Deal", on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    issued_on = models.DateField(default=timezone.localdate)
    due_on = models.DateField()
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))])
    total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"), editable=False)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_invoices")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_on", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["workspace", "number"], name="uniq_invoice_workspace_number"),
        ]
        indexes = [
            models.Index(fields=["workspace", "status"]),
            models.Index(fields=["workspace", "due_on"]),
        ]

    def save(self, *args, **kwargs):
        self.total = (self.subtotal or Decimal("0.00")) + (self.tax or Decimal("0.00"))
        if not self.currency and self.workspace_id:
            self.currency = self.workspace.currency
        super().save(*args, **kwargs)

    @property
    def paid_amount(self) -> Decimal:
        return sum((payment.amount for payment in self.payments.all()), Decimal("0.00"))

    @property
    def outstanding(self) -> Decimal:
        return max(self.total - self.paid_amount, Decimal("0.00"))

    @property
    def is_overdue(self) -> bool:
        return self.status not in {"paid", "void"} and self.due_on < timezone.localdate()

    def __str__(self) -> str:
        return f"{self.number} · {self.company.name}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ("bank_transfer", "Bank transfer"),
        ("card", "Card"),
        ("cash", "Cash"),
        ("other", "Other"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="payments")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    paid_on = models.DateField(default=timezone.localdate)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="bank_transfer")
    reference = models.CharField(max_length=120, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_payments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_on", "-created_at"]
        indexes = [models.Index(fields=["workspace", "paid_on"])]

    def __str__(self) -> str:
        return f"{self.invoice.number} · {self.amount}"


class RevenueEvent(models.Model):
    KIND_CHOICES = [
        ("deal_won", "Deal won"),
        ("expansion", "Expansion"),
        ("renewal", "Renewal"),
        ("refund", "Refund"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="revenue_events")
    deal = models.ForeignKey("crm.Deal", on_delete=models.PROTECT, related_name="revenue_events")
    campaign = models.ForeignKey("marketing.Campaign", on_delete=models.SET_NULL, null=True, blank=True, related_name="revenue_events")
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="revenue_events")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="deal_won")
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    recognized_on = models.DateField(default=timezone.localdate)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recognized_on", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["workspace", "deal", "kind"], name="uniq_revenue_event_deal_kind"),
        ]
        indexes = [
            models.Index(fields=["workspace", "recognized_on"]),
            models.Index(fields=["workspace", "campaign"]),
        ]

    def __str__(self) -> str:
        return f"{self.deal.name} · {self.amount}"
