"""
POS Full — managed operations models.

Managed Django ORM models (app_label="pos_full").
Replaces the previously deleted posapp Rust-mirror models.
"""

from __future__ import annotations

from django.db import models


class KitchenStation(models.Model):
    """A kitchen prep station that tickets route to (grill, fry, prep, bar, …)."""

    STATION_TYPES = [
        ("expedite", "Expedite"),
        ("grill", "Grill"),
        ("fry", "Fry"),
        ("prep", "Prep"),
        ("bar", "Bar"),
        ("pantry", "Pantry"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    station_type = models.CharField(
        max_length=40, choices=STATION_TYPES, default="expedite"
    )
    category_keywords = models.TextField(
        blank=True, default="",
        help_text="Comma-separated category name keywords used for auto-routing tickets.",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_kitchen_stations"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class KitchenTicket(models.Model):
    """Kitchen display system tickets linked to sales."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("delivered", "Delivered"),
    ]

    sale = models.ForeignKey(
        "Sale", on_delete=models.CASCADE, related_name="kitchen_tickets"
    )
    station = models.ForeignKey(
        KitchenStation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
        help_text="Station this ticket is routed to.",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.IntegerField(default=0)
    prepare_time_minutes = models.IntegerField(default=15, help_text="Estimated preparation time in minutes")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_kitchen_tickets"
        ordering = ["-priority", "created_at"]

    def __str__(self) -> str:
        return f"Kitchen Ticket #{self.id} — Sale #{self.sale_id}"


class SupportTicket(models.Model):
    """Customer/user support tickets submitted via the in-app chat widget."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_support_tickets"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.status}] {self.subject} — {self.name}"


def route_station_for_sale(sale) -> KitchenStation | None:
    """Determine the kitchen station a sale's tickets should route to.

    Matches each sale item's product category name (falling back to the item's
    free-text ``product_name``) against each active station's comma-separated
    ``category_keywords``. If nothing matches, falls back to the first active
    ``expedite`` station, then any active station, then ``None``.
    """
    from .pos import SaleItem  # lazy import to avoid a models/pos ↔ ops cycle

    # Precompute keyword → station mapping once.
    keyword_stations: list[tuple[KitchenStation, list[str]]] = []
    for station in KitchenStation.objects.filter(is_active=True).order_by("sort_order", "name"):
        kws = [
            k.strip().lower()
            for k in (station.category_keywords or "").split(",")
            if k.strip()
        ]
        if kws:
            keyword_stations.append((station, kws))

    names: list[str] = []
    items = sale.items.all() if hasattr(sale, "items") else SaleItem.objects.filter(sale=sale)
    for item in items.select_related("product__category"):
        if item.product and item.product.category:
            names.append(item.product.category.name.lower())
        elif item.product_name:
            names.append(item.product_name.lower())

    for station, kws in keyword_stations:
        if any(any(kw in name for kw in kws) for name in names):
            return station

    return (
        KitchenStation.objects.filter(is_active=True, station_type="expedite").first()
        or KitchenStation.objects.filter(is_active=True).first()
    )
