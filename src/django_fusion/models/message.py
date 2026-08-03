"""Abstract Message base model for Fusion sites."""

import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AbstractMessage(models.Model):
    """Abstract base for communication messages between entities."""

    class MessageTypeChoices(models.TextChoices):
        GENERAL = "general", _("General")
        SYSTEM = "system", _("System")
        NOTIFICATION = "notification", _("Notification")
        ALERT = "alert", _("Alert")
        SUPPORT = "support", _("Support")

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SENT = "sent", _("Sent")
        DELIVERED = "delivered", _("Delivered")
        READ = "read", _("Read")
        FAILED = "failed", _("Failed")

    object_id = models.UUIDField(default=uuid.uuid4, editable=False)

    sender_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_sent_messages",
    )
    sender_object_id = models.UUIDField()
    sender_content_object = GenericForeignKey("sender_content_type", "sender_object_id")

    recipient_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_received_messages",
    )
    recipient_object_id = models.UUIDField()
    recipient_content_object = GenericForeignKey("recipient_content_type", "recipient_object_id")

    subject = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True)

    message_type = models.CharField(
        max_length=15,
        choices=MessageTypeChoices.choices,
        default=MessageTypeChoices.GENERAL,
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )
    priority = models.PositiveSmallIntegerField(default=1)

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    replied_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
    )

    has_attachments = models.BooleanField(default=False)

    # created_at provided by BaseModel
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sender_content_type", "sender_object_id"]),
            models.Index(fields=["recipient_content_type", "recipient_object_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_read"]),
            models.Index(fields=["priority", "created_at"]),
        ]

    def __str__(self):
        return f"{self.subject} - {self.sender_content_object} to {self.recipient_content_object}"

    def send(self):
        if self.status == self.StatusChoices.DRAFT:
            self.status = self.StatusChoices.SENT
            self.sent_at = timezone.now()
            self.save()

    def mark_as_delivered(self):
        if self.status == self.StatusChoices.SENT:
            self.status = self.StatusChoices.DELIVERED
            self.delivered_at = timezone.now()
            self.save()

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            if self.status == self.StatusChoices.DELIVERED:
                self.status = self.StatusChoices.READ
            self.save()
