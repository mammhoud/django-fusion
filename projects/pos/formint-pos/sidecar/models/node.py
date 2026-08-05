"""
POS Full Node Registry models — Node, Heartbeat, NodeEvent.
"""

from __future__ import annotations

from django.db import models


class Node(models.Model):
    """Registered POS node in the network (Full edition as cloud master)."""

    NODE_TYPES = [
        ("pos-minimal", "POS Minimal"), ("pos-solo", "POS Solo"),
        ("pos-full", "POS Full"), ("custom", "Custom"),
    ]
    STATUS_CHOICES = [
        ("online", "Online"), ("offline", "Offline"),
        ("degraded", "Degraded"), ("maintenance", "Maintenance"),
        ("unknown", "Unknown"),
    ]

    node_id = models.CharField(max_length=100, unique=True)
    hostname = models.CharField(max_length=255, blank=True, default="")
    node_type = models.CharField(max_length=20, choices=NODE_TYPES, default="pos-minimal")
    version = models.CharField(max_length=50, blank=True, default="unknown")
    api_version = models.CharField(max_length=20, blank=True, default="1.0")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="online", db_index=True)
    status_message = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)
    product_count = models.IntegerField(default=0)
    transaction_count = models.IntegerField(default=0)
    customer_count = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    capabilities = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True, db_index=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_full"
        db_table = "full_nodes"
        ordering = ["-last_seen"]
        indexes = [
            models.Index(fields=["status", "last_seen"]),
            models.Index(fields=["node_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.node_id} ({self.status})"

    def mark_offline(self, reason: str = "") -> None:
        self.status = "offline"
        self.status_message = reason
        self.save(update_fields=["status", "status_message", "updated_at"])

    def mark_online(self, message: str = "") -> None:
        was_offline = self.status == "offline"
        self.status = "online"
        self.status_message = message
        self.save(update_fields=["status", "status_message", "updated_at"])


class Heartbeat(models.Model):
    """Audit log of every heartbeat received from a node."""

    node_id = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20, default="online")
    payload = models.JSONField(default=dict, blank=True)
    latency_ms = models.FloatField(blank=True, null=True)
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_heartbeats"
        ordering = ["-received_at"]
        indexes = [models.Index(fields=["node_id", "received_at"])]

    def __str__(self) -> str:
        return f"❤️ {self.node_id}"


class NodeEvent(models.Model):
    """Significant events in a node's lifecycle."""

    EVENT_TYPES = [
        ("registered", "Registered"), ("heartbeat", "Heartbeat Received"),
        ("status_change", "Status Change"), ("heartbeat_lost", "Heartbeat Lost"),
        ("heartbeat_restored", "Heartbeat Restored"), ("deleted", "Deleted"),
        ("config_change", "Configuration Change"),
        ("sync_success", "Cloud Sync Success"), ("sync_failed", "Cloud Sync Failed"),
        ("error", "Error"),
    ]

    node_id = models.CharField(max_length=100, db_index=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    description = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_node_events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["node_id", "event_type"]),
            models.Index(fields=["event_type"]),
        ]

    def __str__(self) -> str:
        return f"[{self.event_type}] {self.node_id}"
