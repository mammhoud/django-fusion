"""
Portfolio Admin — django-unfold
Registers Project and PortfolioTag with full Unfold ModelAdmin.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models.snippets.project import Project
from .models.snippets.tag import PortfolioTag


# ── PortfolioTag ──────────────────────────────────────────────────────────────

@admin.register(PortfolioTag)
class PortfolioTagAdmin(ModelAdmin):
    list_display = ["name", "slug", "display_color", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ["name"]}
    list_editable = ["is_active"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (_("Tag Info"), {
            "fields": ("name", "slug", "description"),
        }),
        (_("Display"), {
            "fields": ("color", "icon", "is_active"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @display(description=_("Color"), label=True)
    def display_color(self, obj):
        return obj.color or "—"


# ── Project ───────────────────────────────────────────────────────────────────

@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = [
        "title",
        "category",

        "is_active",
        "date_completed",
    ]
    list_filter = ["is_active", "category", "date_completed"]
    search_fields = ["title", "description", "category"]
    prepopulated_fields = {"slug": ["title"]}
    list_editable = ["is_active"]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["tags"]
    date_hierarchy = "date_completed"
    fieldsets = (
        (_("Basic Information"), {
            "fields": ("title", "slug", "category"),
        }),
        (_("Content"), {
            "fields": ("description", "body", "image"),
        }),
        (_("Media & Links"), {
            "fields": ("video_url", "project_url", "tools", "date_completed"),
        }),
        (_("Tags"), {
            "fields": ("tags",),
        }),
        (_("Visibility"), {
            "fields": ("is_active",),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
