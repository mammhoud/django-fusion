"""
Transaction models — Sales, SaleDetails, and Purchases.

Adapted from original crm/transactions/models.py:
- Sale / SaleDetail / Purchase inherit from BaseModel (UUID pk)
- FKs now point to new plugin model paths
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from django_fusion.core.models.base import BaseModel

DELIVERY_CHOICES = [("P", "Pending"), ("S", "Successful")]


class Sale(BaseModel):
    """A completed sale transaction."""

    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_("Sale Date"))
    customer = models.ForeignKey(
        "crm_accounts.Customer",
        on_delete=models.DO_NOTHING,
        related_name="sales",
        verbose_name=_("Customer"),
    )
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percentage = models.FloatField(default=0.0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["-date_added"]
        verbose_name = _("Sale")
        verbose_name_plural = _("Sales")

    def __str__(self) -> str:
        return f"Sale #{self.id} — {self.grand_total} ({self.date_added:%Y-%m-%d})"

    def sum_products(self) -> int:
        return sum(d.quantity for d in self.details.all())


class SaleDetail(models.Model):
    """A line item within a sale."""

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="details")
    item = models.ForeignKey(
        "crm_inventory.Item", on_delete=models.DO_NOTHING, related_name="sale_details"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_detail = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Sale Detail")
        verbose_name_plural = _("Sale Details")

    def __str__(self) -> str:
        return f"{self.item.name} × {self.quantity}"


class Purchase(BaseModel):
    """A purchase order from a vendor."""

    slug = AutoSlugField(unique=True, populate_from="vendor")
    item = models.ForeignKey(
        "crm_inventory.Item", on_delete=models.CASCADE, related_name="purchases"
    )
    description = models.TextField(max_length=300, blank=True, null=True)
    vendor = models.ForeignKey(
        "crm_accounts.Vendor",
        related_name="purchases",
        on_delete=models.CASCADE,
    )
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Delivery Date"))
    quantity = models.PositiveIntegerField(default=0)
    delivery_status = models.CharField(
        choices=DELIVERY_CHOICES, max_length=1, default="P", verbose_name=_("Delivery Status")
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("Price per item")
    )
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["-order_date"]
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")

    def save(self, *args, **kwargs):
        self.total_value = self.price * self.quantity
        super().save(*args, **kwargs)
        # Update stock
        self.item.quantity += self.quantity
        self.item.save(update_fields=["quantity", "updated_at"])

    def __str__(self) -> str:
        return f"Purchase: {self.item.name} from {self.vendor.name}"
