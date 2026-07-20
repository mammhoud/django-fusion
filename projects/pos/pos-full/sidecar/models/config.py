"""
POS Full configuration models — DeviceConfig, MasterDevice, CloudLink.
"""

from __future__ import annotations

from django.db import models


class DeviceConfig(models.Model):
    """Key-value configuration entry for a device/node in the network."""

    CONFIG_CATEGORIES = [
        ("system", "System"),
        ("network", "Network"),
        ("sync", "Sync & Cloud"),
        ("app", "Application"),
        ("hardware", "Hardware"),
        ("security", "Security"),
        ("custom", "Custom"),
    ]

    node_id = models.CharField(max_length=100, db_index=True)
    config_key = models.CharField(max_length=200)
    config_value = models.JSONField(default=dict, blank=True)
    category = models.CharField(
        max_length=50, choices=CONFIG_CATEGORIES, default="system",
    )
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    version = models.IntegerField(default=1, help_text="Configuration version marker")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_device_configs"
        unique_together = [("node_id", "config_key")]
        ordering = ["node_id", "config_key"]
        verbose_name = "device configuration"

    def __str__(self) -> str:
        return f"{self.node_id}/{self.config_key} (v{self.version})"


class MasterDevice(models.Model):
    """Master device that manages other devices/nodes in the network."""

    DEVICE_TYPES = [
        ("cloud_server", "Cloud Server"),
        ("local_controller", "Local Controller"),
        ("gateway", "Gateway"),
        ("master_node", "Master Node"),
    ]
    STATUS_CHOICES = [
        ("online", "Online"),
        ("offline", "Offline"),
        ("degraded", "Degraded"),
        ("maintenance", "Maintenance"),
    ]

    name = models.CharField(max_length=200)
    device_id = models.CharField(max_length=100, unique=True)
    node_id = models.CharField(max_length=100, blank=True, default="")
    device_type = models.CharField(
        max_length=50, choices=DEVICE_TYPES, default="cloud_server",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="online", db_index=True,
    )
    status_message = models.TextField(blank=True, default="")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    api_version = models.CharField(max_length=20, blank=True, default="1.0")
    capabilities = models.JSONField(default=dict, blank=True)
    config = models.JSONField(default=dict, blank=True, help_text="Full configuration snapshot")
    managed_node_ids = models.JSONField(
        default=list, blank=True,
        help_text="List of node_ids this master device manages",
    )
    is_active = models.BooleanField(default=True)
    last_heartbeat_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_master_devices"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["device_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.device_id}) — {self.status}"


class CloudLink(models.Model):
    """Cloud connection configuration for syncing data to an external CRM/master."""

    STATUS_CHOICES = [
        ("connected", "Connected"),
        ("disconnected", "Disconnected"),
        ("error", "Error"),
        ("connecting", "Connecting"),
    ]

    name = models.CharField(max_length=200)
    cloud_url = models.URLField(max_length=500)
    api_key = models.CharField(max_length=500, blank=True, default="")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default="disconnected", db_index=True,
    )
    status_message = models.TextField(blank=True, default="")
    is_primary = models.BooleanField(default=False, help_text="Primary cloud connection for sync")
    sync_interval = models.IntegerField(default=60, help_text="Sync interval in seconds")
    last_connected_at = models.DateTimeField(blank=True, null=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default="pending", choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")])

    class Meta:
        app_label = "pos_full"
        db_table = "full_cloud_links"
        ordering = ["-is_primary", "name"]
        verbose_name = "cloud link"

    def __str__(self) -> str:
        return f"{self.name} ({self.cloud_url}) — {self.status}"
