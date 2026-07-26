import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fusion.models.base import BaseModel as DefaultBase


class Message(DefaultBase):
    """
    Message model for communication between entities.
    """

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

    # Sender (generic foreign key)
    sender_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="%(app_label)s_sent_messages"
    )
    sender_object_id = models.UUIDField()
    sender_content_object = GenericForeignKey("sender_content_type", "sender_object_id")

    # Recipient (generic foreign key)
    recipient_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="%(app_label)s_received_messages"
    )
    recipient_object_id = models.UUIDField()
    recipient_content_object = GenericForeignKey("recipient_content_type", "recipient_object_id")

    # Message content
    subject = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True)

    # Message metadata
    message_type = models.CharField(
        max_length=15, choices=MessageTypeChoices.choices, default=MessageTypeChoices.GENERAL
    )
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, default=StatusChoices.DRAFT
    )
    priority = models.PositiveSmallIntegerField(default=1)  # 1=Low, 2=Normal, 3=High, 4=Urgent

    # Tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    replied_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies"
    )

    # Attachments
    has_attachments = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [  # noqa: RUF012
            models.Index(fields=["sender_content_type", "sender_object_id"]),
            models.Index(fields=["recipient_content_type", "recipient_object_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_read"]),
            models.Index(fields=["priority", "created_at"]),
        ]
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def __str__(self):
        return f"{self.subject} - {self.sender_content_object} to {self.recipient_content_object}"

    def send(self):
        """Send the message."""
        if self.status == self.StatusChoices.DRAFT:
            self.status = self.StatusChoices.SENT
            self.sent_at = timezone.now()
            self.save()

    def mark_as_delivered(self):
        """Mark message as delivered."""
        if self.status == self.StatusChoices.SENT:
            self.status = self.StatusChoices.DELIVERED
            self.delivered_at = timezone.now()
            self.save()

    def mark_as_read(self):
        """Mark message as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            if self.status == self.StatusChoices.DELIVERED:
                self.status = self.StatusChoices.READ
            self.save()

    def reply(self, content, subject=None):
        """Create a reply to this message."""
        if not subject:
            subject = f"Re: {self.subject}"

        reply = Message.objects.create(
            sender_content_object=self.recipient_content_object,
            recipient_content_object=self.sender_content_object,
            subject=subject,
            content=content,
            replied_to=self,
            status=self.StatusChoices.DRAFT,
        )
        return reply

    @property
    def is_replied(self):
        """Check if message has been replied to."""
        return self.replies.exists()

    def generate_summary(self):
        """Generate summary from content."""
        if not self.summary and self.content:
            sentences = self.content.split(".")
            self.summary = ".".join(sentences[:2]) + "."
            self.save()
