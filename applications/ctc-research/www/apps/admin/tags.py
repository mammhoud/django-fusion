"""
Django admin configuration for tagging system.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from ..models.tags import Tag, TaggedItem


class TaggedItemInline(TabularInline):
    model = TaggedItem
    extra = 0
    readonly_fields = ("content_type", "object_id", "tagged_by", "tagged_at")
    fields = ("content_type", "object_id", "tagged_by", "tagged_at")
    verbose_name = _("Tagged Item")
    verbose_name_plural = _("Tagged Items")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    """Admin interface for Tag model."""

    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True
    list_display = ("name", "slug", "created_at", "tag_count")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "tag_count")
    inlines = [TaggedItemInline]

    fieldsets = (
        (_("Basic Information"), {
            "fields": ("name", "slug", "description")
        }),
        (_("Metadata"), {
            "fields": ("created_at", "updated_at", "tag_count"),
            "classes": ("collapse",)
        }),
    )

    def tag_count(self, obj):
        return obj.tagged_items.count()
    tag_count.short_description = _("Number of Tagged Items")


@admin.register(TaggedItem)
class TaggedItemAdmin(ModelAdmin):
    """Admin interface for TaggedItem model."""

    compressed_fields = True
    list_filter_submit = True
    list_display = ("tag", "content_type", "object_id", "tagged_by", "tagged_at")
    list_filter = ("tag", "content_type", "tagged_at")
    search_fields = ("tag__name", "object_id")
    readonly_fields = ("tagged_at", "content_object")

    fieldsets = (
        (_("Tag Information"), {
            "fields": ("tag", "content_type", "object_id", "content_object")
        }),
        (_("Tracking"), {
            "fields": ("tagged_by", "tagged_at"),
            "classes": ("collapse",)
        }),
    )

    def has_add_permission(self, request):
        return False
