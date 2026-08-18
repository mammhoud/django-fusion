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
from django.utils.translation import gettext_lazy as _

from apps.core.models import Workspace


class PosSale(models.Model):
    PAYMENT_METHODS = [
        ("cash", _("Cash")),
        ("card", _("Card")),
        ("mobile", _("Mobile")),
        ("mixed", _("Mixed")),
        ("credit", _("Store Credit")),
    ]
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("completed", _("Completed")),
        ("refunded", _("Refunded")),
        ("cancelled", _("Cancelled")),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="pos_sales", verbose_name=_("workspace"))
    contact = models.ForeignKey(
        "crm.Contact", on_delete=models.SET_NULL, null=True, blank=True, related_name="pos_sales", verbose_name=_("contact")
    )
    external_id = models.CharField(max_length=120, verbose_name=_("external id"))
    sale_date = models.DateTimeField(default=timezone.now, verbose_name=_("sale date"))
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))], verbose_name=_("subtotal"))
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))], verbose_name=_("tax amount"))
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))], verbose_name=_("discount amount"))
    cashback_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))], verbose_name=_("cashback amount"))
    total = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))], verbose_name=_("total"))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="cash", verbose_name=_("payment method"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed", verbose_name=_("status"))
    source = models.CharField(max_length=40, default="formint-pro", verbose_name=_("source"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("metadata"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))

    class Meta:
        ordering = ["-sale_date", "-id"]
        verbose_name = _("POS sale")
        verbose_name_plural = _("POS sales")
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
    pos_sale = models.ForeignKey(PosSale, on_delete=models.CASCADE, related_name="items", verbose_name=_("POS sale"))
    external_id = models.CharField(max_length=120, blank=True, default="", verbose_name=_("external id"))
    product_name = models.CharField(max_length=200, verbose_name=_("product name"))
    quantity = models.IntegerField(verbose_name=_("quantity"))
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))], verbose_name=_("unit price"))
    line_total = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))], verbose_name=_("line total"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        ordering = ["id"]
        verbose_name = _("POS sale item")
        verbose_name_plural = _("POS sale items")
        constraints = [
            models.UniqueConstraint(fields=["pos_sale", "external_id"], name="uniq_pos_sale_item_external"),
        ]

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product_name}"


class PosPayment(models.Model):
    pos_sale = models.ForeignKey(PosSale, on_delete=models.CASCADE, related_name="payments", verbose_name=_("POS sale"))
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name=_("amount"))
    method = models.CharField(max_length=20, choices=PosSale.PAYMENT_METHODS, default="cash", verbose_name=_("method"))
    reference = models.CharField(max_length=120, blank=True, default="", verbose_name=_("reference"))
    paid_on = models.DateField(default=timezone.localdate, verbose_name=_("paid on"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        ordering = ["-paid_on", "-id"]
        verbose_name = _("POS payment")
        verbose_name_plural = _("POS payments")
        indexes = [models.Index(fields=["pos_sale", "paid_on"])]

    def __str__(self) -> str:
        return f"{self.pos_sale.external_id} · {self.amount}"
