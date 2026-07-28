"""
Inventory models — adapted from the original CRM store app.

Changes vs original:
- Inherit from django_fusion BaseModel (UUID pk, created_at/updated_at)
- AutoSlugField retained
- Vendor FK moved to accounts_app
"""
from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.forms import model_to_dict
from django_extensions.db.fields import AutoSlugField

from django_fusion.core.models.base import BaseModel


class Category(BaseModel):
    """A product category."""

    name = models.CharField(max_length=50)
    slug = AutoSlugField(unique=True, populate_from="name")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Item(BaseModel):
    """An inventory item / product."""

    slug = AutoSlugField(unique=True, populate_from="name")
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=256)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="items"
    )
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expiring_date = models.DateTimeField(null=True, blank=True)
    vendor = models.ForeignKey(
        "crm_accounts.Vendor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Items"

    def __str__(self) -> str:
        return f"{self.name} (qty: {self.quantity})"

    def get_absolute_url(self) -> str:
        return reverse("item-detail", kwargs={"slug": self.slug})

    def to_json(self) -> dict:
        product = model_to_dict(self)
        product["id"] = str(self.id)
        product["text"] = self.name
        product["category"] = self.category.name
        product["quantity"] = 1
        product["total_product"] = 0
        product["price"] = float(self.price)
        return product


class Delivery(BaseModel):
    """A delivery of an item to a customer."""

    item = models.ForeignKey(
        Item, blank=True, null=True, on_delete=models.SET_NULL, related_name="deliveries"
    )
    customer_name = models.CharField(max_length=60, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    location = models.CharField(max_length=80, blank=True, null=True)
    date = models.DateTimeField()
    is_delivered = models.BooleanField(default=False, verbose_name="Is Delivered")

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Deliveries"

    def __str__(self) -> str:
        return f"Delivery of {self.item} to {self.customer_name} on {self.date:%Y-%m-%d}"
