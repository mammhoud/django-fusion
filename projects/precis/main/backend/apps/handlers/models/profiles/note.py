import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fusion.models.base import BaseModel as DefaultBase
from django_fusion.models.note import AbstractNote, AbstractSharedNote
from django_fusion.models.tags import *


class Note(AbstractNote, DefaultBase):
    """Concrete Note model — inherits fields from AbstractNote."""

    class Meta(AbstractNote.Meta):
        abstract = False
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def add_tag(self, tag_name, color=None):
        tag, created = Tag.objects.get_or_create(
            name=tag_name, defaults={"color": color or "#3B82F6"}
        )
        self.tags.add(tag)
        return tag

    def share_with(self, users):
        if self.visibility == "private":
            self.visibility = "shared"
            self.save()
        for user in users:
            SharedNote.objects.get_or_create(note=self, user=user, can_edit=False)

    def generate_summary(self):
        sentences = self.content.split(".")
        self.summary = ".".join(sentences[:3]) + "."
        self.save()


class SharedNote(AbstractSharedNote, DefaultBase):
    """Concrete SharedNote model — inherits fields from AbstractSharedNote."""

    class Meta(AbstractSharedNote.Meta):
        abstract = False
        verbose_name = _("Shared Note")
        verbose_name_plural = _("Shared Notes")
