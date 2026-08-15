"""Loop-CRM POS ingestion ledger.

Formint POS transactions (sales, line items, payments) land here through the
machine-to-machine ingest road. The ledger is deliberately separate from the
deal-linked ``finance.Invoice``/``Payment``/``RevenueEvent`` models: a POS sale
is a B2C transaction, not a B2B invoice, and keeping them apart preserves the
invoice state machine while a ``RevenueEvent`` bridge carries POS money into the
existing trend/attribution queries.
"""
from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import Workspace


class PosSale(models.Model):
    PAYMENT_METHODS = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("mobile", "Mobile"),
        ("mixed", "Mixed"),
        ("credit", "Store Credit"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("refunded", "Refunded"),
        ("cancelled", "Cancelled"),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="pos_sales")
    contact = models.ForeignKey(
        "crm.Contact", on_delete=models.SET_NULL, null=True, blank=True, related_name="pos_sales"
    )
    external_id = models.CharField(max_length=120)
    sale_date = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))])
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))])
    cashback_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))])
    total = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="cash")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")
    source = models.CharField(max_length=40, default="formint-pro")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-sale_date", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["workspace", "external_id"], name="uniq_pos_sale_workspace_external"),
        ]
        indexes = [
            models.Index(fields=["workspace", "sale_date"]),
            models.Index(fields=["workspace", "status"]),
        ]

    def __str__(self) -> str:
        return f"POS sale {self.external_id} · {self.total}"


class PosSaleItem(models.Model):
    pos_sale = models.ForeignKey(PosSale, on_delete=models.CASCADE, related_name="items")
    external_id = models.CharField(max_length=120, blank=True, default="")
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    line_total = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["pos_sale", "external_id"], name="uniq_pos_sale_item_external"),
        ]

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product_name}"


class PosPayment(models.Model):
    pos_sale = models.ForeignKey(PosSale, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    method = models.CharField(max_length=20, choices=PosSale.PAYMENT_METHODS, default="cash")
    reference = models.CharField(max_length=120, blank=True, default="")
    paid_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_on", "-id"]
        indexes = [models.Index(fields=["pos_sale", "paid_on"])]

    def __str__(self) -> str:
        return f"{self.pos_sale.external_id} · {self.amount}"
