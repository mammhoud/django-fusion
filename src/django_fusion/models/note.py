"""Abstract Note and SharedNote base models for Fusion sites."""

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AbstractNote(models.Model):
    """Abstract base for user-generated notes with tagging support."""

    class VisibilityChoices(models.TextChoices):
        PRIVATE = "private", _("Private")
        SHARED = "shared", _("Shared")
        PUBLIC = "public", _("Public")

    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True)

    # Generic foreign key to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
    )
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Relationships
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(app_label)s_created_notes",
    )

    # Metadata
    visibility = models.CharField(
        max_length=10,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PRIVATE,
    )
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    # Timestamps (created_at/updated_at provided by BaseModel)
    pinned_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]  # created_at provided by BaseModel
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["is_pinned", "created_at"]),
            models.Index(fields=["is_archived"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_pinned and not self.pinned_at:
            self.pinned_at = timezone.now()
        elif not self.is_pinned:
            self.pinned_at = None
        if self.is_archived and not self.archived_at:
            self.archived_at = timezone.now()
        elif not self.is_archived:
            self.archived_at = None
        super().save(*args, **kwargs)

    @property
    def excerpt(self):
        return self.content[:150] + "..." if len(self.content) > 150 else self.content


class AbstractSharedNote(models.Model):
    """Abstract base for tracking shared notes with specific users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    note = models.ForeignKey(
        "Note",
        on_delete=models.CASCADE,
        related_name="shared_with",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_shared_notes",
    )
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    shared_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        unique_together = ["note", "user"]
        ordering = ["-shared_at"]

    def __str__(self):
        return f"{self.note} shared with {self.user}"

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return self.expires_at < timezone.now()
