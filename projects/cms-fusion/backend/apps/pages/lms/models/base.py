"""
Local replacements for ceptor_ai base models.

These stubs exist so that CMS/LMS models can inherit from ContentBase
and ModelCacheMixin without depending on the ceptor_ai app, which has
deep migration conflicts (duplicate db_tables with the shared app).

The public surface mirrors ceptor_ai.content.models.default.ContentBase
and ceptor_ai.content.models.cache.ModelCacheMixin.
"""

from __future__ import annotations

import logging
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fusion.models.base import BaseModel as DefaultBase

logger = logging.getLogger(__name__)


# ---- ContentBase -----------------------------------------------------------


class TemplateRenderMixin:
    """Stub — migration compatibility only."""

    pass


class EnhancedBase(DefaultBase, TemplateRenderMixin):
    """Minimal version of ceptor_ai's EnhancedBase."""

    version = models.PositiveIntegerField(default=1, verbose_name=_("Version"))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.version += 1
        super().save(*args, **kwargs)


class ContentBase(EnhancedBase):
    """Abstract base for content types with publishing fields.

    Fields mirror ceptor_ai.content.models.default.ContentBase so that
    existing model subclasses (e.g. Classes) can inherit without change.
    """

    title = models.CharField(
        max_length=200,
        verbose_name=_("Title"),
        help_text=_("The title of the content."),
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Subtitle"),
        help_text=_("Optional subtitle."),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A brief description of the content."),
    )
    excerpt = models.TextField(
        blank=True,
        verbose_name=_("Excerpt"),
        help_text=_("Short excerpt for previews and listings."),
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("Display order (lower numbers first)."),
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_("Is Published"),
        help_text=_("Whether the content is published and visible."),
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Published At"),
        help_text=_("When this content was published."),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("Internal notes about this content."),
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return getattr(self, "title", "") or super().__str__()


# ---- ModelCacheMixin -------------------------------------------------------


class ModelCacheMixin:
    """Minimal version of ceptor_ai's ModelCacheMixin.

    Provides cache_key / cache_set / cache_get / get_or_cache helpers.
    Production deployments should wire a real cache backend; this stub
    simply logs and returns None for all cache operations.
    """

    @property
    def cache_key(self) -> str:
        return f"{self.__class__.__name__.lower()}:{self.pk or id(self)}"

    def cache_set(self, timeout: int | None = None) -> bool:
        return False

    @classmethod
    def cache_get(cls, identifier: Any) -> Any | None:
        return None

    @classmethod
    def get_or_cache(cls, identifier: Any, **kwargs) -> Any | None:
        return None

    def invalidate_all_cache(self) -> int:
        return 0
