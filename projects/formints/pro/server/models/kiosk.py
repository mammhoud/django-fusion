"""
POS Full — self-checkout kiosk models.

A self-service kiosk session holds a touchscreen cart (``KioskCartItem``
lines snapshotting product name + unit price) before checkout. On checkout
the cart is handed to the canonical ``sale_checkout`` surface, which creates
the ``Sale`` / ``SaleItem`` / ``KitchenTicket``; the session then links the
sale and closes itself.
"""

from __future__ import annotations

from django.db import models


class KioskSession(models.Model):
    """A self-service checkout session (kiosk mode)."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("checked_out", "Checked Out"),
        ("cancelled", "Cancelled"),
    ]

    session_key = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=100, default="", blank=True,
                            help_text="Friendly kiosk label (e.g. 'Kiosk 1').")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    sale = models.ForeignKey(
        "Sale", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="kiosk_sessions",
        help_text="Sale created when this session checked out.",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[("cash", "Cash"), ("card", "Card"), ("mobile", "Mobile"),
                 ("mixed", "Mixed"), ("credit", "Store Credit")],
        default="card",
        help_text="Default payment method for kiosk checkout.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_kiosk_sessions"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"KioskSession {self.session_key} [{self.status}]"


class KioskCartItem(models.Model):
    """A line in a kiosk session's cart (pre-checkout)."""

    session = models.ForeignKey(
        KioskSession, on_delete=models.CASCADE, related_name="cart_items"
    )
    product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="kiosk_cart_items",
    )
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_kiosk_cart_items"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product_name}"

    @property
    def line_total(self) -> float:
        return float(self.unit_price) * self.quantity
