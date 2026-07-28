"""Invoice model — adapted to use BaseModel and plugin FK paths."""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from django_fusion.core.models.base import BaseModel


class Invoice(BaseModel):
    """An invoice for a sale to a named customer."""

    slug = AutoSlugField(unique=True, populate_from="date")
    date = models.DateTimeField(auto_now=True, verbose_name=_("Date"))
    customer_name = models.CharField(max_length=80, verbose_name=_("Customer Name"))
    contact_number = models.CharField(max_length=30, verbose_name=_("Contact Number"))
    item = models.ForeignKey(
        "crm_inventory.Item",
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name=_("Item"),
    )
    price_per_item = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Price Per Item")
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("Quantity")
    )
    shipping = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Shipping")
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, verbose_name=_("Total")
    )
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, verbose_name=_("Grand Total")
    )

    class Meta:
        ordering = ["-date"]
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    def save(self, *args, **kwargs):
        self.total = round(self.quantity * self.price_per_item, 2)
        self.grand_total = round(self.total + self.shipping, 2)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Invoice #{self.slug} — {self.customer_name}"
