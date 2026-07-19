"""
Cloud Sync — Synchronization Models for POS Cloud CRM.

Tracks sync operations, queued changes, and cloud configuration
for the CRM module between the local sidecar and the cloud server.

Architecture:
  sidecar (local POS)  ↔  HTTP REST  ↔  cloud server (shared-portal/cloud/)

Sync flow:
  1. Sidecar creates/updates/deletes CRM entities
  2. Changes recorded in SyncQueue
  3. Cloud server processes queue periodically
  4. SyncLog tracks outcome of each sync operation

Related Names: sync, cloud, crm, sync_log, sync_queue, cloud_config
Tags: #sync #cloud #crm #models #pos-full
"""

from django.db import models


class SyncLog(models.Model):
    """Tracks every sync operation between local sidecar and cloud CRM server.

    Each entry records one sync attempt for one entity.
    Failed entries can be retried up to max_retries times.

    Use Cases:
      - Audit trail for all CRM data synchronization
      - Debugging sync failures
      - Monitoring sync health and latency
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("skipped", "Skipped"),
    ]

    entity_type = models.TextField(
        help_text="Entity type: contact, company, deal, activity, note, pipeline"
    )
    entity_id = models.IntegerField(
        help_text="Local database ID of the entity being synced"
    )
    cloud_id = models.TextField(
        null=True, blank=True,
        help_text="Cloud CRM entity ID after successful sync"
    )
    action = models.TextField(
        choices=[("create", "Create"), ("update", "Update"), ("delete", "Delete")]
    )
    status = models.TextField(default="pending", choices=STATUS_CHOICES)
    error_message = models.TextField(
        null=True, blank=True,
        help_text="Error details if sync failed"
    )
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    duration_ms = models.IntegerField(
        null=True, blank=True,
        help_text="Sync duration in milliseconds"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crm_sync_log"
        managed = True
        ordering = ["-created_at"]
        verbose_name = "Sync Log"
        verbose_name_plural = "Sync Logs"
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type} #{self.entity_id} — {self.status}"


class SyncQueue(models.Model):
    """Queue of changes waiting to be synced to/from the cloud CRM server.

    Each entry represents one change (create/update/delete) to one entity.
    The cloud server processor picks up pending items in priority order.

    Use Cases:
      - Offline change queue (POS works offline, syncs when connected)
      - Conflict resolution queue (cloud vs local changes)
      - Batch sync processing
    """

    PRIORITY_CHOICES = [
        (1, "High"),
        (2, "Normal"),
        (3, "Low"),
    ]

    entity_type = models.TextField()
    entity_id = models.IntegerField()
    action = models.TextField(
        choices=[("create", "Create"), ("update", "Update"), ("delete", "Delete")]
    )
    payload = models.JSONField(
        default=dict, help_text="Serialized entity data for sync"
    )
    direction = models.TextField(
        default="local_to_cloud",
        choices=[("local_to_cloud", "Local → Cloud"), ("cloud_to_local", "Cloud → Local")],
        help_text="Direction of sync"
    )
    priority = models.IntegerField(default=2, choices=PRIORITY_CHOICES)
    is_processing = models.BooleanField(default=False)
    error_count = models.IntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crm_sync_queue"
        managed = True
        ordering = ["priority", "created_at"]
        indexes = [
            models.Index(fields=["is_processing"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type} #{self.entity_id} [{self.direction}]"


class CloudConfig(models.Model):
    """Configuration for cloud CRM connection and sync behavior.

    Stored as a single row (singleton pattern). Controls
    sync frequency, authentication, and server endpoints.

    Use Cases:
      - Connecting POS to a cloud CRM server
      - Configuring sync intervals and retry behavior
      - Managing API credentials securely
    """

    SYNC_INTERVAL_CHOICES = [
        (30, "Every 30 seconds"),
        (60, "Every minute"),
        (300, "Every 5 minutes"),
        (900, "Every 15 minutes"),
        (3600, "Every hour"),
        (0, "Manual only"),
    ]

    sync_enabled = models.BooleanField(default=False)
    cloud_url = models.URLField(
        null=True, blank=True,
        help_text="Cloud CRM API base URL (e.g. http://localhost:8766 or https://crm.example.com)"
    )
    api_key = models.TextField(
        null=True, blank=True,
        help_text="API key for cloud CRM authentication"
    )
    sync_interval = models.IntegerField(
        default=60, choices=SYNC_INTERVAL_CHOICES,
        help_text="Seconds between sync attempts"
    )
    retry_max = models.IntegerField(default=3, help_text="Maximum retry attempts per item")
    retry_delay = models.IntegerField(default=5, help_text="Seconds between retries")
    conflict_strategy = models.TextField(
        default="local_wins",
        choices=[("local_wins", "Local Wins"), ("cloud_wins", "Cloud Wins"),
                 ("latest_wins", "Latest Wins"), ("manual", "Manual Resolution")],
        help_text="Strategy for resolving sync conflicts"
    )
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.TextField(
        null=True, blank=True,
        help_text="Status of last sync attempt"
    )
    last_sync_summary = models.TextField(
        null=True, blank=True,
        help_text="Summary of last sync: items synced, errors, etc."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crm_cloud_config"
        managed = True
        verbose_name = "Cloud Configuration"

    def __str__(self) -> str:
        return f"Cloud Sync: {'Enabled' if self.sync_enabled else 'Disabled'}"
