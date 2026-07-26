"""
Local DefaultBase — wraps django_fusion.models.base.BaseModel with
additional audit and publish fields not provided by the library.

django-fusion BaseModel provides:
  - id (UUIDField, pk)
  - created_at (DateTimeField, auto_now_add, db_index)
  - updated_at (DateTimeField, auto_now)

This local stub adds:
  - created_by / updated_by (FK to AUTH_USER_MODEL)
  - is_active
  - live / first_published_at / last_published_at (Wagtail publish compat)
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fusion.models.base import BaseModel as FusionBaseModel


class DefaultBase(FusionBaseModel):
    """
    Abstract base model extending django_fusion's BaseModel with
    audit fields (created_by, updated_by), is_active flag, and
    Wagtail publish-compatible fields (live, first/last_published_at).
    """

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
