"""
Moderated approval workflow model — SyncApproval.

Tracks changes (sales, reports, config updates, product changes)
that require moderation before being applied to the database.
"""

from __future__ import annotations

from django.db import models


class SyncApproval(models.Model):
    """Pending data change that requires moderator approval before applying."""

    ENTITY_TYPES = [
        ("sale", "Sale"),
        ("product", "Product"),
        ("config", "Configuration"),
        ("report", "Report"),
        ("inventory", "Inventory"),
        ("customer", "Customer"),
        ("employee", "Employee"),
        ("category", "Category"),
        ("sync", "Sync Batch"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("applied", "Applied to DB"),
        ("failed", "Apply Failed"),
    ]

    # Source
    node_id = models.CharField(max_length=100, db_index=True)
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES)
    entity_id = models.CharField(max_length=200, blank=True, default="")

    # The change data (what was pushed)
    change_data = models.JSONField(default=dict, blank=True)
    change_summary = models.CharField(max_length=500, blank=True, default="")

    # Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True,
    )

    # Moderation
    reviewed_by = models.CharField(max_length=100, blank=True, default="")
    review_notes = models.TextField(blank=True, default="")
    reviewed_at = models.DateTimeField(blank=True, null=True)

    # Error tracking
    error_message = models.TextField(blank=True, default="")
    retry_count = models.IntegerField(default=0)

    # Direction
    SYNC_DIRECTION_CHOICES = [
        ("push", "Push from Node"),
        ("pull", "Pull by Master"),
        ("sync", "Bidirectional Sync"),
    ]
    direction = models.CharField(
        max_length=10, choices=SYNC_DIRECTION_CHOICES, default="push",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pos_unified"
        db_table = "pos_sync_approvals"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["node_id", "status"]),
            models.Index(fields=["entity_type", "status"]),
            models.Index(fields=["status"]),
        ]
        verbose_name = "sync approval"
        verbose_name_plural = "sync approvals"

    def __str__(self) -> str:
        return f"[{self.status}] {self.entity_type}/{self.entity_id} from {self.node_id}"

    def approve(self, reviewer: str = "", notes: str = "") -> None:
        """Mark this approval as approved."""
        self.status = "approved"
        self.reviewed_by = reviewer
        self.review_notes = notes
        self.reviewed_at = __import__("django").utils.timezone.now()
        self.save(update_fields=["status", "reviewed_by", "review_notes", "reviewed_at", "updated_at"])

    def reject(self, reviewer: str = "", notes: str = "") -> None:
        """Mark this approval as rejected."""
        self.status = "rejected"
        self.reviewed_by = reviewer
        self.review_notes = notes
        self.reviewed_at = __import__("django").utils.timezone.now()
        self.save(update_fields=["status", "reviewed_by", "review_notes", "reviewed_at", "updated_at"])

    def mark_applied(self, error: str = "") -> None:
        """Mark this approval as successfully applied to the database."""
        self.status = "applied" if not error else "failed"
        self.error_message = error
        self.save(update_fields=["status", "error_message", "updated_at"])
