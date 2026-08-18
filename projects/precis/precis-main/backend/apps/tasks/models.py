"""Landing-Fusion task models.

``TaskExecution`` is the website-local mirror of django-fusion's shared
``BackgroundTaskLog`` audit record. The shared worker writes the shared record;
the Task Center page mirrors it into this product-owned table (idempotent on
``job_id``) so the site can query its own task history without reaching the
shared-infra database.
"""

from django.db import models
from django.utils import timezone


class TaskExecution(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("started", "Started"),
        ("finished", "Finished"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("retrying", "Retrying"),
    ]

    job_id = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    task_name = models.CharField(max_length=255, db_index=True)
    queue_name = models.CharField(max_length=100, default="default")
    site_name = models.CharField(max_length=100, db_index=True, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["site_name", "-created_at"]),
            models.Index(fields=["task_name", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.task_name} [{self.status}]"
