"""
Custom tagging system for Django models.

Provides a flexible tagging system that allows any model to be tagged
with user tracking and filtering capabilities.
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """
    Represents a tag that can be applied to various models.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("The name of the tag")
    )
    slug = models.SlugField(
        unique=True,
        help_text=_("URL-friendly version of the tag name")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Optional description of the tag")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class TaggedItem(models.Model):
    """
    Through model for tagging any object in the system.

    Uses Django's ContentType framework to allow tagging of any model.
    """
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tagged_items'
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Tracking information
    tagged_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tagged_items',
        help_text=_("User who added this tag")
    )
    tagged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Tagged Item")
        verbose_name_plural = _("Tagged Items")
        unique_together = ('tag', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['tag']),
        ]

    def __str__(self):
        return f"{self.tag.name} - {self.content_object}"


class TagManager(models.Manager):
    """
    Custom manager for models that support tagging.
    """

    def get_queryset(self):
        """Return the base queryset."""
        return super().get_queryset()

    def with_tags(self):
        """Prefetch tags for better performance."""
        from django.db.models import Prefetch
        return self.prefetch_related(
            Prefetch('tags')
        )

    def filter_by_tag(self, tag_name):
        """Filter objects by a specific tag name."""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(self.model)
        tagged_ids = TaggedItem.objects.filter(
            tag__name=tag_name,
            content_type=content_type
        ).values_list('object_id', flat=True)
        return self.filter(id__in=tagged_ids)

    def filter_by_tags(self, tag_names, match_all=False):
        """
        Filter objects by multiple tags.

        Args:
            tag_names: List of tag names
            match_all: If True, object must have all tags. If False, any tag.
        """
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(self.model)

        if match_all:
            # Object must have all tags
            queryset = self
            for tag_name in tag_names:
                tagged_ids = TaggedItem.objects.filter(
                    tag__name=tag_name,
                    content_type=content_type
                ).values_list('object_id', flat=True)
                queryset = queryset.filter(id__in=tagged_ids)
            return queryset
        else:
            # Object can have any of the tags
            tagged_ids = TaggedItem.objects.filter(
                tag__name__in=tag_names,
                content_type=content_type
            ).values_list('object_id', flat=True).distinct()
            return self.filter(id__in=tagged_ids)

    def search_by_tags(self, search_term):
        """Search for tags by name or description."""
        from django.contrib.contenttypes.models import ContentType
        from django.db.models import Q

        content_type = ContentType.objects.get_for_model(self.model)
        tags = Tag.objects.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term)
        )
        tagged_ids = TaggedItem.objects.filter(
            tag__in=tags,
            content_type=content_type
        ).values_list('object_id', flat=True).distinct()
        return self.filter(id__in=tagged_ids)
