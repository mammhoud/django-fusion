"""
POS Solo sync log model — SyncLog.
"""

from __future__ import annotations

from django.db import models


class SyncLog(models.Model):
    """Audit log for data sync operations to cloud master."""

    SYNC_STATUS_CHOICES = [
        ("pending", "Pending"), ("in_progress", "In Progress"),
        ("success", "Success"), ("failed", "Failed"),
    ]
    SYNC_DIRECTION_CHOICES = [("push", "Push to Cloud"), ("pull", "Pull from Cloud")]

    node_id = models.CharField(max_length=100, db_index=True)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100, blank=True, default="")
    direction = models.CharField(max_length=10, choices=SYNC_DIRECTION_CHOICES, default="push")
    status = models.CharField(max_length=20, choices=SYNC_STATUS_CHOICES, default="pending", db_index=True)
    payload_size = models.IntegerField(blank=True, null=True)
    duration_ms = models.IntegerField(blank=True, null=True)
    error_message = models.TextField(blank=True, default="")
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_unified"
        db_table = "unified_sync_logs"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["node_id", "status"])]

    def __str__(self) -> str:
        return f"[{self.direction}] {self.entity_type}/{self.entity_id} — {self.status}"
