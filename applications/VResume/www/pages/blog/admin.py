"""
Blog Admin — django-unfold
Registers BlogTag, BlogAuthor, BlogPost with full Unfold ModelAdmin.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import BlogTag, BlogAuthor, ArticleRead, ArticleEngagement
from .models.snippets.post import BlogPost


# ── BlogTag ───────────────────────────────────────────────────────────────────

@admin.register(BlogTag)
class BlogTagAdmin(ModelAdmin):
    list_display = ["name", "slug", "category", "display_color", "is_active", "display_order"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "description", "category"]
    prepopulated_fields = {"slug": ["name"]}
    list_editable = ["is_active", "display_order"]
    fieldsets = (
        (_("Basic Info"), {
            "fields": ("name", "slug", "description", "category"),
        }),
        (_("Display"), {
            "fields": ("color", "icon", "display_order", "is_active"),
        }),
    )

    @display(description=_("Color"), label=True)
    def display_color(self, obj):
        return obj.color or "—"


# ── BlogAuthor ────────────────────────────────────────────────────────────────

@admin.register(BlogAuthor)
class BlogAuthorAdmin(ModelAdmin):
    list_display = ["name", "role", "email", "is_active", "display_order"]
    list_filter = ["is_active"]
    search_fields = ["name", "role", "email", "bio"]
    prepopulated_fields = {"slug": ["name"]}
    list_editable = ["is_active", "display_order"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (_("Identity"), {
            "fields": ("name", "slug", "role", "photo"),
        }),
        (_("Bio"), {
            "fields": ("bio",),
        }),
        (_("Contact & Social"), {
            "fields": ("email", "website", "twitter", "linkedin"),
        }),
        (_("Settings"), {
            "fields": ("is_active", "display_order"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


# ── BlogPost ──────────────────────────────────────────────────────────────────

@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = [
        "title",
        "is_published",
        "published_date",
        "reading_time",
        "page_views",
    ]
    list_filter = ["is_published", "published_date"]
    search_fields = ["title", "subtitle", "introduction"]
    prepopulated_fields = {"slug": ["title"]}
    list_editable = ["is_published"]
    readonly_fields = ["page_views", "reading_time", "created_at", "updated_at"]
    date_hierarchy = "published_date"
    filter_horizontal = ["tags", "related_posts"]
    fieldsets = (
        (_("Content"), {
            "fields": (
                "title", "slug", "subtitle",
                "introduction", "excerpt",
                "featured_image", "published_date",
                "body",
            ),
        }),
        (_("Authors & Tags"), {
            "fields": ("tags",),
        }),
        (_("Publication"), {
            "fields": ("is_published", "display_order"),
        }),
        (_("SEO"), {
            "fields": ("meta_title", "meta_description", "canonical_url", "og_image"),
            "classes": ("collapse",),
        }),
        (_("Analytics"), {
            "fields": ("reading_time", "page_views"),
            "classes": ("collapse",),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


# ── ArticleRead ───────────────────────────────────────────────────────────────

@admin.register(ArticleRead)
class ArticleReadAdmin(ModelAdmin):
    list_display = [
        "post",
        "ip_address",
        "read_duration_seconds",
        "scroll_depth",
        "is_unique",
        "read_at",
    ]
    list_filter = ["is_unique", "read_at"]
    search_fields = ["post__title", "ip_address", "session_key"]
    readonly_fields = ["read_at", "post"]
    date_hierarchy = "read_at"
    fieldsets = (
        (_("Article"), {
            "fields": ("post",),
        }),
        (_("Reader Info"), {
            "fields": ("session_key", "ip_address"),
        }),
        (_("Engagement"), {
            "fields": ("read_duration_seconds", "scroll_depth", "is_unique"),
        }),
        (_("Timestamp"), {
            "fields": ("read_at",),
        }),
    )

    def has_add_permission(self, request):
        return False
    
    @display(description=_("Engagement Score"))
    def engagement_score(self, obj):
        return obj.engagement_score


# ── ArticleEngagement ─────────────────────────────────────────────────────────

@admin.register(ArticleEngagement)
class ArticleEngagementAdmin(ModelAdmin):
    list_display = [
        "post",
        "engagement_score",
        "unique_readers",
        "reads",
        "likes",
        "shares",
        "updated_at",
    ]
    list_filter = ["updated_at"]
    search_fields = ["post__title"]
    readonly_fields = [
        "post",
        "engagement_score",
        "updated_at",
    ]
    fieldsets = (
        (_("Article"), {
            "fields": ("post",),
        }),
        (_("Engagement Metrics"), {
            "fields": ("likes", "shares", "bookmarks"),
        }),
        (_("Read Metrics"), {
            "fields": (
                "unique_readers",
                "reads",
            ),
        }),
        (_("Score"), {
            "fields": ("engagement_score",),
        }),
        (_("Timestamp"), {
            "fields": ("updated_at",),
        }),
    )

    def has_add_permission(self, request):
        return False
