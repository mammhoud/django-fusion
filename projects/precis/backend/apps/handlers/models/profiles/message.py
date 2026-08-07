"""Concrete Message model — inherits fields from AbstractMessage."""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fusion.models.base import BaseModel as DefaultBase
from django_fusion.models.message import AbstractMessage


class Message(AbstractMessage, DefaultBase):
    """Concrete Message model for communication between entities."""

    class Meta(AbstractMessage.Meta):
        abstract = False
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def reply(self, content, subject=None):
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
        return self.replies.exists()

    def generate_summary(self):
        if not self.summary and self.content:
            sentences = self.content.split(".")
            self.summary = ".".join(sentences[:2]) + "."
            self.save()
