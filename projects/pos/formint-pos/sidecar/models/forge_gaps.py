"""
POS Full — Managed models closing gap with forge-pos.

Django ORM models (app_label="pos_full") for features that exist in
forge-pos but were missing from the formint-pos merged package:

  * Coupon          — discount/promo codes for checkout
  * DeliveryType    — delivery method catalog (dine-in, takeaway, delivery)
  * DeliveryZone    — geographic zones with per-km pricing
  * Shift           — cash register shift open/close tracking

Each model mirrors the corresponding Diesel schema in forge-pos so the
data authority (Django) is a superset.
"""

from __future__ import annotations

from django.db import models


class Coupon(models.Model):
    """Discount / promo code applicable to sales at checkout.

    Mirrors ``forge-pos/src-tauri/src/db/models.rs::Coupon`` and the
    Diesel migration at ``2026-08-05-000001_create_coupons/up.sql``.
    """

    KIND_CHOICES = [
        ("percent", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField(max_length=50, unique=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="percent")
    value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Discount value: percentage (e.g. 10 = 10%) or fixed amount",
    )
    min_subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Minimum cart subtotal for the coupon to apply",
    )
    max_uses = models.IntegerField(
        null=True, blank=True,
        help_text="Max number of times this coupon can be used (null = unlimited)",
    )
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_coupons"
        ordering = ["-created_at"]
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self) -> str:
        return f"{self.code} ({self.get_kind_display()}: {self.value})"

    def is_valid_for_subtotal(self, subtotal: float) -> bool:
        """Check whether the coupon applies to a given cart subtotal."""
        if not self.is_active:
            return False
        if self.min_subtotal is not None and subtotal < float(self.min_subtotal):
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        return True


class DeliveryType(models.Model):
    """Delivery method catalog (dine-in, takeaway, delivery, etc.).

    Mirrors ``forge-pos/src-tauri/src/db/models.rs::DeliveryType``.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    fee_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.0,
        help_text="Multiplier applied to the base delivery fee (1.0 = standard)",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_delivery_types"
        ordering = ["name"]
        verbose_name = "Delivery Type"
        verbose_name_plural = "Delivery Types"

    def __str__(self) -> str:
        return self.name


class DeliveryZone(models.Model):
    """Geographic delivery zone with distance-based pricing.

    Mirrors ``forge-pos/src-tauri/src/db/models.rs::DeliveryZone``.
    """

    name = models.CharField(max_length=100, unique=True)
    base_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0,
        help_text="Flat fee for any delivery within this zone",
    )
    fee_per_km = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0,
        help_text="Additional fee per kilometer beyond the base",
    )
    max_distance = models.DecimalField(
        max_digits=8, decimal_places=2, default=10.0,
        help_text="Maximum distance (km) this zone covers; requests beyond are rejected",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_delivery_zones"
        ordering = ["name"]
        verbose_name = "Delivery Zone"
        verbose_name_plural = "Delivery Zones"

    def __str__(self) -> str:
        return f"{self.name} (${self.base_fee} + ${self.fee_per_km}/km, max {self.max_distance}km)"

    def calculate_fee(self, distance_km: float) -> float | None:
        """Calculate the delivery fee for a given distance.

        Returns ``None`` if the distance exceeds ``max_distance``.
        """
        if distance_km > float(self.max_distance):
            return None
        return float(self.base_fee) + (distance_km * float(self.fee_per_km))


class Shift(models.Model):
    """Cash register shift — open/close cycle with cash tracking.

    Mirrors ``forge-pos/src-tauri/src/operations/shifts.rs``.

    At any time, at most one shift can be "open".  Opening a shift
    records the starting cash float; closing it captures the ending
    cash and an auto-computed expected amount based on sales during
    the shift window.
    """

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]

    employee = models.ForeignKey(
        "Employee", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="shifts",
        help_text="Employee who opened the shift",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    opening_cash = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0,
        help_text="Cash float at shift open",
    )
    closing_cash = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Actual cash counted at shift close",
    )
    expected_cash = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Auto-computed expected cash based on sales during shift",
    )
    notes = models.TextField(blank=True, default="")
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_shifts"
        ordering = ["-opened_at"]
        verbose_name = "Shift"
        verbose_name_plural = "Shifts"
        constraints = [
            # Only one open shift at a time (enforced at DB level)
            models.UniqueConstraint(
                fields=["status"],
                condition=models.Q(status="open"),
                name="unique_open_shift",
            ),
        ]

    def __str__(self) -> str:
        emp = self.employee or "Unknown"
        return f"Shift #{self.id} ({emp}, {self.status})"

    @property
    def duration_hours(self) -> float | None:
        """Elapsed hours; None if still open."""
        if self.closed_at is None:
            return None
        delta = self.closed_at - self.opened_at
        return delta.total_seconds() / 3600


# ── Auto-register in the central model registry ──

__all__ = ["Coupon", "DeliveryType", "DeliveryZone", "Shift"]
