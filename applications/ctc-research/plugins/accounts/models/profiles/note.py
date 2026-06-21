import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_osoul.models import BaseModel as DefaultBase
from crafts_ai.models.tags import *


class Note(DefaultBase):
    """
    Note model for user-generated notes.
    """

    class VisibilityChoices(models.TextChoices):
        PRIVATE = "private", _("Private")
        SHARED = "shared", _("Shared")
        PUBLIC = "public", _("Public")

    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True)

    # Generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Relationships
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_notes"
    )
    # tags = models.ManyToManyField(Tag, blank=True, related_name="notes")

    # Metadata
    visibility = models.CharField(
        max_length=10, choices=VisibilityChoices.choices, default=VisibilityChoices.PRIVATE
    )
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pinned_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["is_pinned", "created_at"]),
            models.Index(fields=["is_archived"]),
        ]
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Update timestamps for pinning/archiving
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
        """Get excerpt of content."""
        return self.content[:150] + "..." if len(self.content) > 150 else self.content

    def add_tag(self, tag_name, color=None):
        """Add a tag to the note."""
        tag, created = Tag.objects.get_or_create(
            name=tag_name, defaults={"color": color or "#3B82F6"}
        )
        self.tags.add(tag)
        return tag

    def share_with(self, users):
        """Share note with specific users."""
        if self.visibility == "private":
            self.visibility = "shared"
            self.save()

        # Create shared instances
        for user in users:
            SharedNote.objects.get_or_create(note=self, user=user, can_edit=False)

    def generate_summary(self):
        """Generate automatic summary of content."""
        # Simple implementation - first 3 sentences
        sentences = self.content.split(".")
        self.summary = ".".join(sentences[:3]) + "."
        self.save()


class SharedNote(DefaultBase):
    """
    Model for tracking shared notes with specific users.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    note = models.ForeignKey("Note", on_delete=models.CASCADE, related_name="shared_with")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shared_notes"
    )
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    shared_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["note", "user"]
        ordering = ["-shared_at"]
        verbose_name = _("Shared Note")
        verbose_name_plural = _("Shared Notes")

    def __str__(self):
        return f"{self.note} shared with {self.user}"

    @property
    def is_expired(self):
        """Check if sharing has expired."""
        if not self.expires_at:
            return False
        return self.expires_at < timezone.now()
