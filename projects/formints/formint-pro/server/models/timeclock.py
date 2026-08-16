"""
POS Full — Time-clock tracking model (P3, Professional).

Employee scheduling companion: ``EmployeeSchedule`` (in ``models/hr.py``)
holds the weekly shift plan; ``TimeClockEntry`` records the *actual*
clock-in/clock-out punches with break minutes, so worked hours and payroll
can be computed from reality rather than the plan.

* ``TimeClockEntry`` — one punch pair: ``clock_in``, optional ``clock_out``,
  accumulated ``break_minutes``, and an optional ``schedule`` link back to
  the shift that was planned for that day.

Carries the standard sync-tracking fields (``is_synced`` / ``synced_at`` /
``sync_status``) so it participates in the multi-terminal changeset
collector alongside the rest of the pos_full app.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class TimeClockEntry(models.Model):
    """A clock-in/clock-out pair for an employee."""

    employee = models.ForeignKey(
        "Employee", on_delete=models.CASCADE, related_name="timeclock_entries",
    )
    schedule = models.ForeignKey(
        "EmployeeSchedule", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="timeclock_entries",
        help_text="The planned shift this punch corresponds to (if any).",
    )
    clock_in = models.DateTimeField(default=timezone.now)
    clock_out = models.DateTimeField(null=True, blank=True)
    break_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Accumulated break time in minutes for this shift.",
    )
    note = models.CharField(max_length=255, blank=True, default="")
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
        db_table = "full_timeclock_entries"
        ordering = ["-clock_in"]
        indexes = [
            models.Index(fields=["employee", "clock_in"]),
            models.Index(fields=["clock_out"]),
        ]

    def __str__(self) -> str:
        return f"{self.employee} in {self.clock_in:%Y-%m-%d %H:%M}"

    @property
    def is_active(self) -> bool:
        return self.clock_out is None

    @property
    def worked_minutes(self) -> int | None:
        """Gross minutes on shift minus breaks; None while still open."""
        if self.clock_out is None:
            return None
        delta = self.clock_out - self.clock_in
        gross = max(int(delta.total_seconds() // 60), 0)
        return max(gross - self.break_minutes, 0)

    @property
    def worked_hours(self) -> float | None:
        minutes = self.worked_minutes
        if minutes is None:
            return None
        return round(minutes / 60, 2)
