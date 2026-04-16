"""
Custom tagging system for the handlers app.

Provides Tag, TaggedItem, and TagManager for generic content tagging.
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class TagManager(models.Manager):
    """Custom manager for Tag model with filtering and search support."""

    def get_queryset(self):
        return super().get_queryset()

    def with_tags(self):
        """Return queryset with prefetched tags."""
        return self.get_queryset().prefetch_related("tagged_items")

    def filter_by_tag(self, tag_name):
        """Filter objects by a single tag name."""
        content_type = ContentType.objects.get_for_model(self.model)
        tagged_ids = TaggedItem.objects.filter(
            tag__name=tag_name,
            content_type=content_type,
        ).values_list("object_id", flat=True)
        return self.get_queryset().filter(pk__in=tagged_ids)

    def filter_by_tags(self, tag_names, match_all=False):
        """Filter objects by multiple tag names.

        Args:
            tag_names: list of tag name strings
            match_all: if True, object must have ALL tags; if False, ANY tag
        """
        content_type = ContentType.objects.get_for_model(self.model)
        if match_all:
            qs = self.get_queryset()
            for name in tag_names:
                ids = TaggedItem.objects.filter(
                    tag__name=name,
                    content_type=content_type,
                ).values_list("object_id", flat=True)
                qs = qs.filter(pk__in=ids)
            return qs
        else:
            tagged_ids = TaggedItem.objects.filter(
                tag__name__in=tag_names,
                content_type=content_type,
            ).values_list("object_id", flat=True)
            return self.get_queryset().filter(pk__in=tagged_ids).distinct()

    def search_by_tags(self, query):
        """Search objects by tag name or description."""
        content_type = ContentType.objects.get_for_model(self.model)
        tagged_ids = TaggedItem.objects.filter(
            content_type=content_type,
        ).filter(
            models.Q(tag__name__icontains=query) | models.Q(tag__description__icontains=query)
        ).values_list("object_id", flat=True)
        return self.get_queryset().filter(pk__in=tagged_ids).distinct()


class Tag(models.Model):
    """Generic tag model for content tagging."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self):
        return self.name


class TaggedItem(models.Model):
    """Through model linking a Tag to any content object."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tagged_items",
        verbose_name=_("Tag"),
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content Type"),
    )
    object_id = models.PositiveIntegerField(verbose_name=_("Object ID"))
    content_object = GenericForeignKey("content_type", "object_id")
    tagged_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tagged_items",
        verbose_name=_("Tagged By"),
    )
    tagged_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Tagged At"))

    class Meta:
        verbose_name = "Tagged Item"
        verbose_name_plural = "Tagged Items"
        unique_together = [["tag", "content_type", "object_id"]]

    def __str__(self):
        return f"{self.tag.name} → {self.content_object}"
