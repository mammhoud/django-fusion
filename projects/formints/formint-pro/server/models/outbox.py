"""
POS Full — outbound offline queue (OutboxQueue).

Offline Queue (P1, Community+): transactions are recorded locally even when
the cloud master is unreachable, then flushed when connectivity returns.

``OutboxQueue`` is the durable record of an outbound operation — the entity
type, id, action, and a JSON snapshot of the payload at enqueue time — plus
its retry state (``retry_count``, ``max_retries``, exponential-backoff
``available_at``). Rows that exhaust their retries are dead-lettered
(``status="dead"``) for operator review instead of retried forever.
"""

from __future__ import annotations

from django.db import models


class OutboxQueue(models.Model):
    """Durable outbound operation queue for offline-first sync."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_flight", "In Flight"),
        ("done", "Done"),
        ("failed", "Failed"),
        ("dead", "Dead Letter"),
    ]

    node_id = models.CharField(max_length=100, default="", blank=True, db_index=True)
    entity_type = models.CharField(max_length=50, db_index=True)
    entity_id = models.CharField(max_length=100, blank=True, default="")
    action = models.CharField(max_length=20, default="push")
    payload = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=10)
    last_error = models.TextField(blank=True, default="")
    available_at = models.DateTimeField(null=True, blank=True,
                                        help_text="Backoff — don't retry before this time")
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_outbox_queue"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["status", "available_at"]),
            models.Index(fields=["node_id", "entity_type"]),
        ]

    def __str__(self) -> str:
        return f"[{self.status}] {self.entity_type}/{self.entity_id or '?'} (retry {self.retry_count}/{self.max_retries})"
