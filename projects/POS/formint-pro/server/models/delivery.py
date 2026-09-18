"""
POS Full — Delivery Integration models (P2, Professional+).

Connectors for delivery platforms (Talabat, HungerStation) and outbound
delivery-order tracking:

* ``DeliveryProvider`` — a platform connector registration (name, enabled,
                         API endpoint/credentials, commission rate).
* ``DeliveryOrder``   — an outbound delivery order: provider, optional
                        linked ``Sale``, customer + address, distance and
                        computed fee (from ``DeliveryZone``), and a status
                        lifecycle driven by the provider webhook or the
                        POS operator.

Both models carry the standard sync-tracking fields (``is_synced`` /
``synced_at`` / ``sync_status``) so they participate in the multi-terminal
changeset collector alongside the rest of the pos_full app.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class DeliveryProvider(models.Model):
    """A delivery platform connector (Talabat, HungerStation, manual…)."""

    PROVIDER_TYPES = [
        ("talabat", "Talabat"),
        ("hungerstation", "HungerStation"),
        ("careem", "Careem Food"),
        ("manual", "Manual / Own Fleet"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("disabled", "Disabled"),
    ]

    name = models.CharField(max_length=100, unique=True)
    provider_type = models.CharField(
        max_length=20, choices=PROVIDER_TYPES, default="manual",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", db_index=True,
    )
    base_url = models.URLField(blank=True, default="")
    api_key = models.CharField(
        max_length=200, blank=True, default="",
        help_text="Provider API credential (kept plaintext for local POS config).",
    )
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0,
        help_text="Platform commission percentage (0–100).",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")],
    )

    class Meta:
        app_label = "pos_full"
        db_table = "full_delivery_providers"
        ordering = ["provider_type", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_provider_type_display()})"


class DeliveryOrder(models.Model):
    """An outbound delivery order dispatched to a provider."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("preparing", "Preparing"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
    ]

    provider = models.ForeignKey(
        DeliveryProvider, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="delivery_orders",
    )
    provider_order_id = models.CharField(
        max_length=100, blank=True, default="",
        help_text="External order id returned by the provider.",
    )
    sale = models.ForeignKey(
        "Sale", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="delivery_orders",
    )
    delivery_type = models.ForeignKey(
        "DeliveryType", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="delivery_orders",
    )
    delivery_zone = models.ForeignKey(
        "DeliveryZone", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="delivery_orders",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True,
    )

    customer_name = models.CharField(max_length=200, blank=True, default="")
    customer_phone = models.CharField(max_length=30, blank=True, default="")
    delivery_address = models.TextField(blank=True, default="")
    distance_km = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        help_text="Distance from the branch to the drop-off point.",
    )
    delivery_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text="Computed fee from the delivery zone (base + per-km).",
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")],
    )

    class Meta:
        app_label = "pos_full"
        db_table = "full_delivery_orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["provider", "status"]),
        ]

    def __str__(self) -> str:
        who = self.customer_name or f"order #{self.pk}"
        return f"{who} → {self.provider} [{self.status}]"
