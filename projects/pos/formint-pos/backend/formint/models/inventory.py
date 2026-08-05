"""
POS Full — managed inventory/supplier models.

Managed Django ORM models (app_label="pos_full").
Replaces the previously deleted posapp Rust-mirror models.
"""

from __future__ import annotations

from django.db import models


class Supplier(models.Model):
    """Vendors / suppliers for products and ingredients."""

    name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")
    tax_id = models.CharField(max_length=50, blank=True, default="")
    payment_terms = models.CharField(max_length=200, blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "formint"
        db_table = "full_suppliers"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class PurchaseOrder(models.Model):
    """Procurement orders from suppliers."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("ordered", "Ordered"),
        ("received", "Received"),
        ("cancelled", "Cancelled"),
    ]

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="purchase_orders"
    )
    reference_number = models.CharField(max_length=100, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "formint"
        db_table = "full_purchase_orders"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"PO #{self.id} — {self.supplier.name}"


class PurchaseOrderItem(models.Model):
    """Line items within a purchase order (products, not raw ingredients)."""

    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="purchase_order_items",
    )
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    received_quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "formint"
        db_table = "full_purchase_order_items"
