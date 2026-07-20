"""
Audit trail model for POS signal events — SignalEvent.

Stores every dispatched signal as a database record for:
  - Audit compliance (who changed what, when)
  - Debugging (trace signal chains)
  - Analytics (signal frequency, patterns)
  - Replay (re-process historical signals)
"""

from __future__ import annotations

from django.db import models


class SignalEvent(models.Model):
    """Immutable audit record of a dispatched signal event.

    Every @receiver handler logs to this table, providing a complete
    audit trail of all POS signal activity. Records are append-only.
    """

    SIGNAL_NAMES = [
        ("config_changed", "Configuration Changed"),
        ("master_device_changed", "Master Device Changed"),
        ("cloud_link_changed", "Cloud Link Changed"),
        ("config_synced", "Configuration Synced"),
        ("device_status_changed", "Device Status Changed"),
    ]

    signal_name = models.CharField(
        max_length=50,
        choices=SIGNAL_NAMES,
        db_index=True,
        help_text="Which signal was fired",
    )
    action = models.CharField(
        max_length=50,
        blank=True,
        default="",
        db_index=True,
        help_text="Action type (created, updated, deleted, approved, etc.)",
    )

    # Core identifiers
    node_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        help_text="Node/device identifier associated with this event",
    )
    resource_id = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="ID of the resource that changed (config_key, device_id, etc.)",
    )

    # Full payload snapshot
    payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete signal kwargs payload",
    )

    # Webhook delivery status
    webhook_status = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Webhook delivery status (sent, failed, skipped, pending)",
    )
    webhook_error = models.TextField(
        blank=True,
        default="",
        help_text="Error message if webhook delivery failed",
    )

    # Timing
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the signal was dispatched",
    )

    class Meta:
        app_label = "pos_signals"
        db_table = "pos_signal_events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["signal_name", "created_at"]),
            models.Index(fields=["node_id", "signal_name"]),
            models.Index(fields=["action", "created_at"]),
        ]
        verbose_name = "signal event"
        verbose_name_plural = "signal events"

    def __str__(self) -> str:
        return f"[{self.signal_name}] {self.action} — {self.node_id or '(global)'}"
