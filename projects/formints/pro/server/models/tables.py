"""
POS Full — Table Management models (P2, Professional+).

Restaurant floor layouts and order tracking:

* ``RestaurantTable``  — a physical table with a section/zone, capacity,
                         status, optional floor-plan position, and the
                         currently seated ``Sale`` (order tracking).
* ``TableReservation`` — a booking for a table: party size, reservation
                         time, status lifecycle (confirmed → seated →
                         completed; cancel/no-show branches).

Both models carry the standard sync-tracking fields (``is_synced`` /
``synced_at`` / ``sync_status``) so they participate in the multi-terminal
changeset collector alongside the rest of the pos_full app.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class RestaurantTable(models.Model):
    """A physical restaurant table on the floor plan."""

    SECTION_CHOICES = [
        ("main", "Main Hall"),
        ("patio", "Patio"),
        ("bar", "Bar"),
        ("terrace", "Terrace"),
        ("private", "Private Room"),
        ("outdoor", "Outdoor"),
    ]
    SHAPE_CHOICES = [
        ("round", "Round"),
        ("rect", "Rectangle"),
        ("square", "Square"),
        ("booth", "Booth"),
    ]
    STATUS_CHOICES = [
        ("free", "Free"),
        ("occupied", "Occupied"),
        ("reserved", "Reserved"),
        ("cleaning", "Cleaning"),
        ("closed", "Closed"),
    ]

    name = models.CharField(
        max_length=100,
        help_text="Display label, e.g. 'T12' or 'Patio 3'.",
    )
    section = models.CharField(
        max_length=20, choices=SECTION_CHOICES, default="main", db_index=True,
    )
    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES, default="rect")
    capacity = models.PositiveIntegerField(
        default=2, help_text="Seats this table can host.",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="free", db_index=True,
    )
    # Floor-plan position (pixels / grid units) for visual layouts.
    pos_x = models.IntegerField(default=0)
    pos_y = models.IntegerField(default=0)
    width = models.PositiveIntegerField(default=1)
    height = models.PositiveIntegerField(default=1)
    # Current order tracking — the open sale seated at this table.
    current_sale = models.ForeignKey(
        "Sale", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tables",
        help_text="The open sale currently seated at this table.",
    )
    notes = models.TextField(blank=True, default="")
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
        db_table = "full_restaurant_tables"
        ordering = ["section", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["section", "name"],
                name="uniq_table_section_name",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "section"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_section_display()}, {self.status})"

    @property
    def occupied_by_sale(self) -> bool:
        return self.status == "occupied" and self.current_sale_id is not None


class TableReservation(models.Model):
    """A table booking with a party size and status lifecycle."""

    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("seated", "Seated"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    ]

    table = models.ForeignKey(
        RestaurantTable, on_delete=models.CASCADE, related_name="reservations",
    )
    customer = models.ForeignKey(
        "Customer", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="table_reservations",
    )
    customer_name = models.CharField(
        max_length=200, blank=True, default="",
        help_text="Booking name when no Customer record is linked.",
    )
    party_size = models.PositiveIntegerField(default=1)
    reservation_time = models.DateTimeField(
        help_text="When the party is expected to arrive.",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="confirmed", db_index=True,
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seated_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")],
    )

    class Meta:
        app_label = "pos_full"
        db_table = "full_table_reservations"
        ordering = ["reservation_time"]
        indexes = [
            models.Index(fields=["status", "reservation_time"]),
        ]

    def __str__(self) -> str:
        name = self.customer_name or (self.customer or "Walk-in")
        return f"{name} @ {self.table.name} ({self.get_status_display()})"

    @property
    def display_name(self) -> str:
        if self.customer_name:
            return self.customer_name
        if self.customer:
            return self.customer.full_name
        return "Walk-in"
