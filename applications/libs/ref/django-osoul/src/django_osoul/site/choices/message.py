from django.db import models
from django.utils.translation import gettext_lazy as _


class ConversationType(models.TextChoices):
    DIRECT = "direct", _("Direct Message")
    GROUP = "group", _("Group Chat")
    BROADCAST = "broadcast", _("Broadcast")


class MessageStatus(models.TextChoices):
    SENT = "sent", _("Sent")
    DELIVERED = "delivered", _("Delivered")
    READ = "read", _("Read")
    FAILED = "failed", _("Failed")
