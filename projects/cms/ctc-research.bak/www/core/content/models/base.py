"""
Local DefaultBase stub for environments where ceptor_ai is not installed.
Provides the same abstract fields as ceptor_ai.content.models.default.DefaultBase.
"""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class DefaultBase(models.Model):
    """
    Abstract base model providing UUID pk, timestamps, audit fields,
    and a live flag – mirrors ceptor_ai.content.models.default.DefaultBase.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        verbose_name=_("Created By"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        verbose_name=_("Updated By"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    live = models.BooleanField(default=True, verbose_name=_("Live"))
    first_published_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("First Published At")
    )
    last_published_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Last Published At")
    )

    class Meta:
        abstract = True
