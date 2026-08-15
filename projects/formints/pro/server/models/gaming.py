"""
POS Full — POS-KO Gaming Center models (P0).

Token-based gaming session support for gaming cafes / LAN centers:

* ``GamingStation``  — a PC/console station with an hourly rate and status.
* ``GamingToken``    — a purchased time package (1hr, day-pass, monthly, …)
                        with a remaining-minutes balance.
* ``GamingSession``  — an active/paused/completed session on a station,
                        consuming time from an optional token.
* ``GamingQueueEntry`` — a waitlist entry with an estimated wait time.

All models carry the standard sync-tracking fields (``is_synced`` /
``synced_at`` / ``sync_status``) so they participate in the multi-terminal
changeset collector alongside the rest of the pos_full app.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class GamingStation(models.Model):
    """A bookable gaming station (PC, console, VR rig, …)."""

    STATION_TYPES = [
        ("pc", "PC"),
        ("console", "Console"),
        ("vr", "VR"),
        ("sim", "Simulator"),
    ]
    STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("maintenance", "Maintenance"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    station_type = models.CharField(max_length=20, choices=STATION_TYPES, default="pc")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="available", db_index=True,
    )
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text="Billing rate per hour (used to compute session cost).",
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
        db_table = "full_gaming_stations"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} [{self.status}]"


class GamingToken(models.Model):
    """A purchased time package (1hr / 3hr / day-pass / monthly)."""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("used", "Used"),
        ("expired", "Expired"),
    ]

    name = models.CharField(max_length=200)
    minutes = models.IntegerField(
        help_text="Total purchased minutes in this token.",
    )
    remaining_minutes = models.IntegerField(
        help_text="Minutes still available on this token.",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", db_index=True,
    )
    sold_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")],
    )

    class Meta:
        app_label = "pos_full"
        db_table = "full_gaming_tokens"
        ordering = ["-sold_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.remaining_minutes}/{self.minutes}m)"

    @property
    def is_exhausted(self) -> bool:
        return self.remaining_minutes <= 0


class GamingSession(models.Model):
    """A time-tracked session on a station, optionally drawing from a token."""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    station = models.ForeignKey(
        GamingStation, on_delete=models.CASCADE, related_name="sessions",
    )
    token = models.ForeignKey(
        GamingToken, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sessions",
    )
    customer = models.ForeignKey(
        "Customer", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="gaming_sessions",
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", db_index=True,
    )
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    # The moment the current active run (re)started — used to accumulate
    # elapsed time across pause/resume boundaries.
    last_resume_at = models.DateTimeField(default=timezone.now)
    active_seconds = models.IntegerField(
        default=0,
        help_text="Accumulated active (non-paused) seconds.",
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Computed cost = active duration × station hourly rate.",
    )
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
        db_table = "full_gaming_sessions"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["station", "status"]),
            models.Index(fields=["status", "started_at"]),
        ]

    def __str__(self) -> str:
        return f"Session #{self.pk} @ {self.station.name} [{self.status}]"


class GamingQueueEntry(models.Model):
    """A waitlist entry for a customer waiting for a station."""

    STATUS_CHOICES = [
        ("waiting", "Waiting"),
        ("assigned", "Assigned"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    customer_name = models.CharField(max_length=200)
    requested_minutes = models.IntegerField(default=60)
    station = models.ForeignKey(
        GamingStation, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="queue_entries",
        help_text="Station assigned once a spot frees up.",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="waiting", db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
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
        db_table = "full_gaming_queue"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Queue #{self.pk} {self.customer_name} [{self.status}]"
