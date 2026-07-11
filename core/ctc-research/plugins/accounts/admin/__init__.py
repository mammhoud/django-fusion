"""
Admin configuration for the handlers app.
"""

from django.contrib import admin

from plugins.accounts.models.tags import Tag, TaggedItem

# Import registration admin to register its models
from .registration import *  # noqa: F401, F403


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tag model."""

    list_display = ["name", "slug", "description", "created_at"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name"]


@admin.register(TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    """Admin interface for TaggedItem model."""

    list_display = ["tag", "content_type", "object_id", "tagged_by", "tagged_at"]
    list_filter = ["content_type", "tag"]
    search_fields = ["tag__name"]
    ordering = ["-tagged_at"]
