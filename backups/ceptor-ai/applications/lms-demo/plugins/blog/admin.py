from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin as BaseImportExportModelAdmin
from unfold.admin import ModelAdmin, TabularInline


class ImportExportModelAdmin(BaseImportExportModelAdmin, ModelAdmin):
    """Combines django-import-export with Unfold styling."""
    pass


from .models import BlogCategory, BlogComment, BlogPost, BlogTag


@admin.register(BlogComment)
class BlogCommentAdmin(ModelAdmin):
    """Admin interface for BlogComment model."""

    compressed_fields = True
    list_display = ("__str__", "author", "post", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("content", "author__username", "post__title")
    readonly_fields = ("created_at",)
    list_editable = ("is_approved",)

    fieldsets = (
        (_("Comment"), {
            "fields": ("post", "author", "content")
        }),
        (_("Moderation"), {
            "fields": ("is_approved",)
        }),
        (_("Metadata"), {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )


class BlogTagInline(TabularInline):
    model = BlogPost.tags.through
    extra = 0
    verbose_name = _("Tag")
    verbose_name_plural = _("Tags")


@admin.register(BlogTag)
class BlogTagAdmin(ImportExportModelAdmin):
    """Admin interface for BlogTag model."""

    compressed_fields = True
    warn_unsaved_changes = True
    list_display = ("name", "slug", "post_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("post_count",)

    fieldsets = (
        (_("Tag Information"), {
            "fields": ("name", "slug")
        }),
        (_("Statistics"), {
            "fields": ("post_count",),
            "classes": ("collapse",)
        }),
    )

    def post_count(self, obj):
        return obj.get_post_count()
    post_count.short_description = _("Number of Posts")


@admin.register(BlogCategory)
class BlogCategoryAdmin(ImportExportModelAdmin):
    """Admin interface for BlogCategory model."""

    compressed_fields = True
    warn_unsaved_changes = True
    list_display = ("name", "slug", "post_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("post_count",)

    fieldsets = (
        (_("Category Information"), {
            "fields": ("name", "slug", "description")
        }),
        (_("Statistics"), {
            "fields": ("post_count",),
            "classes": ("collapse",)
        }),
    )

    def post_count(self, obj):
        return obj.get_post_count()
    post_count.short_description = _("Number of Posts")


@admin.register(BlogPost)
class BlogPostAdmin(ImportExportModelAdmin):
    """Admin interface for BlogPost model."""

    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True
    list_display = ("title", "author", "status", "published_date", "reading_time_display")
    list_filter = ("status", "published_date", "created_at", "categories", "tags")
    search_fields = ("title", "content", "excerpt", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "reading_time_display")
    filter_horizontal = ("categories", "tags")

    fieldsets = (
        (_("Post Information"), {
            "fields": ("title", "slug", "author", "status")
        }),
        (_("Content"), {
            "fields": ("excerpt", "content", "featured_image")
        }),
        (_("Organization"), {
            "fields": ("categories", "tags")
        }),
        (_("Publishing"), {
            "fields": ("published_date",)
        }),
        (_("SEO"), {
            "fields": ("meta_description",),
            "classes": ("collapse",)
        }),
        (_("Metadata"), {
            "fields": ("created_at", "updated_at", "reading_time_display"),
            "classes": ("collapse",)
        }),
    )

    def reading_time_display(self, obj):
        return f"{obj.get_reading_time()} min"
    reading_time_display.short_description = _("Reading Time")
