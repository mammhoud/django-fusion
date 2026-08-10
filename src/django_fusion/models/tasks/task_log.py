from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class BackgroundTaskLog(models.Model):
    """
    Audit trail for every background task execution.
    """
    STATUS_CHOICES = [
        ("queued", _("Queued")),
        ("started", _("Started")),
        ("finished", _("Finished")),
        ("failed", _("Failed")),
        ("cancelled", _("Cancelled")),
        ("retrying", _("Retrying")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_id = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    task_name = models.CharField(max_length=255, db_index=True)
    queue_name = models.CharField(max_length=100, default="default")
    backend = models.CharField(max_length=50, default="dramatiq", blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")

    args = models.JSONField(default=list, blank=True)
    kwargs = models.JSONField(default=dict, blank=True)
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    error_traceback = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)

    scheduled_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_scheduled = models.BooleanField(default=False)

    site_id = models.IntegerField(null=True, blank=True, db_index=True)
    app_label_field = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        app_label = "shared"
        verbose_name = _("Background Task Log")
        verbose_name_plural = _("Background Task Logs")
        ordering = ["-created_at"]
        db_table = "grep_background_task_log"
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["task_name", "-created_at"]),
            models.Index(fields=["queue_name", "status"]),
        ]

    def __str__(self):
        return f"{self.task_name} [{self.status}] @ {self.created_at:%Y-%m-%d %H:%M}"

    @property
    def duration(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
