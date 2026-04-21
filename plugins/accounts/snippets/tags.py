from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from www.apps.accounts.models.tag import (
    BlogTag,
    BlogTagCategory,
    PersonTag,
    PersonTagCategory,
)

from ..base import BaseSnippetViewSet


#@register_snippet
class BlogTagViewSet(BaseSnippetViewSet):
    """
    Admin interface for managing Blog Tags with enhanced features
    """
    model = BlogTag
    icon = "tag"
    menu_label = _("Blog Tags")
    menu_order = 310
    add_to_settings_menu = False
    exclude_from_explorer = False

    # ======================
    # SEARCH & FILTERING
    # ======================
    search_fields = [
        "name",
        "description",
        "meta_title",
        "meta_description",
        "category__name",
    ]

    ordering = ["name"]
    list_per_page = 50

    # ======================
    # TABLE CONFIGURATION
    # ======================
    list_display = [
        "display_tag",
        "display_category",
        "display_color",
        "usage_count_display",
        "published_posts_display",
        "live_status_column",
        "updated_at_column",
    ]

    list_filter = [
        "category",
        "live",
        "category__is_public",
    ]

    list_export = [
        "name",
        "slug",
        "category",
        "color",
        "icon",
        "usage_count",
        "published_posts_count",
        "meta_title",
        "meta_description",
        "live",
        "created_at",
        "updated_at",
    ]

    export_fields = list_export
    csv_filename = "blog_tags_export.csv"

    # ======================
    # FORM CONFIGURATION
    # ======================
    form_fields = [
        "name",
        "category",
        "color",
        "icon",
        "description",
        "meta_title",
        "meta_description",
    ]

    # ======================
    # DISPLAY HELPERS
    # ======================

    @staticmethod
    def display_tag(obj):
        """Display tag with color and icon."""
        icon_html = f'<i class="{obj.icon}"></i> ' if obj.icon else ''
        color_style = f'style="color: {obj.color}"' if obj.color else ''

        url = reverse('blogtags:edit', args=[obj.pk])
        return format_html(
            '<a href="{}" {}><strong>{}{}</strong></a>',
            url,
            color_style,
            icon_html,
            obj.name
        )
    display_tag.short_description = _("Tag")
    display_tag.admin_order_field = "name"

    @staticmethod
    def display_category(obj):
        """Display category with color."""
        if obj.category:
            color_style = f'style="color: {obj.category.color}"' if obj.category.color else ''
            return format_html(
                '<span {}>{}</span>',
                color_style,
                obj.category.name
            )
        return "—"
    display_category.short_description = _("Category")
    display_category.admin_order_field = "category"

    @staticmethod
    def display_color(obj):
        """Display color as a colored circle."""
        if obj.color:
            return format_html(
                '<div style="display: inline-block; width: 20px; height: 20px; '
                'background-color: {}; border-radius: 50%; border: 1px solid #ccc;" '
                'title="{}"></div>',
                obj.color,
                obj.color
            )
        return "—"
    display_color.short_description = _("Color")

    @staticmethod
    def usage_count_display(obj):
        """Display usage count with contextual color."""
        if obj.usage_count == 0:
            badge_class = "w-badge w-badge--critical"
        elif obj.usage_count < 5:
            badge_class = "w-badge w-badge--warning"
        else:
            badge_class = "w-badge w-badge--success"

        return format_html(
            '<span class="{}">{}</span>',
            badge_class,
            obj.usage_count
        )
    usage_count_display.short_description = _("Usage")
    usage_count_display.admin_order_field = "usage_count"

    @staticmethod
    def published_posts_display(obj):
        """Display published posts count."""
        count = obj.published_posts_count
        url = reverse('blogpages:index') + f'?tags__id={obj.pk}'
        return format_html(
            '<a href="{}" class="posts-count-link">{}</a>',
            url,
            f"📝 {count}" if count > 0 else "—"
        )
    published_posts_display.short_description = _("Posts")

    # ======================
    # CUSTOM ACTIONS
    # ======================

    @staticmethod
    def get_extra_actions():
        """Define custom actions for the tag viewset."""
        from wagtail import hooks
        from wagtail.admin.views.pages.bulk_actions.delete import DeleteBulkAction

        @hooks.register('register_bulk_action')
        class UpdateTagUsageStatsBulkAction(DeleteBulkAction):
            """Bulk action to update tag usage statistics."""
            display_name = _("Update usage statistics")
            action_type = "update_tag_stats"
            aria_label = _("Update usage statistics for selected tags")
            template_name = "tags/bulk_actions/update_stats.html"

            def execute(self, objects):
                updated = 0
                for tag in objects:
                    tag.update_usage_stats()
                    updated += 1
                return updated, 0

            def get_success_message(self, num_parent_objects, num_child_objects):
                return _(
                    f"Successfully updated statistics for {num_parent_objects} tags"
                )

        return []

    # ======================
    # CUSTOM VIEWS
    # ======================

    def get_queryset(self, request):
        """Optimize queryset with related data."""
        queryset = super().get_queryset(request)
        return queryset.select_related('category').prefetch_related('tagged_blogs')

    def get_index_view(self):
        """Custom index view with additional context."""
        from .views import BlogTagIndexView
        return BlogTagIndexView

    def get_history_view(self):
        """Custom history view."""
        from .views import BlogTagHistoryView
        return BlogTagHistoryView


#@register_snippet
class BlogTagCategoryViewSet(BaseSnippetViewSet):
    """
    Admin interface for managing Blog Tag Categories
    """
    model = BlogTagCategory
    icon = "folder-open-1"
    menu_label = _("Blog Tag Categories")
    menu_order = 311
    add_to_settings_menu = False

    # ======================
    # SEARCH & FILTERING
    # ======================
    search_fields = [
        "name",
        "slug",
        "description",
    ]

    ordering = ["display_order", "name"]
    list_per_page = 50

    # ======================
    # TABLE CONFIGURATION
    # ======================
    list_display = [
        "display_category",
        "display_color",
        "tag_count_display",
        "published_tag_count_display",
        "is_public_display",
        "live_status_column",
        "updated_at_column",
    ]

    list_filter = [
        "is_public",
        "live",
    ]

    list_export = [
        "name",
        "slug",
        "color",
        "icon",
        "display_order",
        "tag_count",
        "published_tag_count",
        "is_public",
        "live",
        "created_at",
        "updated_at",
    ]

    csv_filename = "blog_tag_categories_export.csv"

    # ======================
    # DISPLAY HELPERS
    # ======================

    @staticmethod
    def display_category(obj):
        """Display category with color and icon."""
        icon_html = f'<i class="{obj.icon}"></i> ' if obj.icon else ''
        color_style = f'style="color: {obj.color}"' if obj.color else ''

        url = reverse('blogtagcategories:edit', args=[obj.pk])
        return format_html(
            '<a href="{}" {}><strong>{} {}</strong></a>',
            url,
            color_style,
            icon_html,
            obj.name
        )
    display_category.short_description = _("Category")
    display_category.admin_order_field = "name"

    @staticmethod
    def display_color(obj):
        """Display color as a colored circle."""
        if obj.color:
            return format_html(
                '<div style="display: inline-block; width: 20px; height: 20px; '
                'background-color: {}; border-radius: 50%; border: 1px solid #ccc;" '
                'title="{}"></div>',
                obj.color,
                obj.color
            )
        return "—"
    display_color.short_description = _("Color")

    @staticmethod
    def tag_count_display(obj):
        """Display total tag count."""
        count = obj.tag_count
        url = reverse('blogtags:index') + f'?category__id={obj.pk}'
        return format_html(
            '<a href="{}" class="tag-count-link">{}</a>',
            url,
            f"🏷️ {count}" if count > 0 else "—"
        )
    tag_count_display.short_description = _("Total Tags")

    @staticmethod
    def published_tag_count_display(obj):
        """Display published tag count."""
        count = obj.published_tag_count
        return format_html(
            '<span class="published-tag-count">{}</span>',
            f"✅ {count}" if count > 0 else "—"
        )
    published_tag_count_display.short_description = _("Published Tags")

    @staticmethod
    def is_public_display(obj):
        """Display public status."""
        if obj.is_public:
            return format_html(
                '<span class="w-badge w-badge--success">🌐 {}</span>',
                _("Public")
            )
        return format_html(
            '<span class="w-badge w-badge--critical">🔒 {}</span>',
            _("Private")
        )
    is_public_display.short_description = _("Visibility")


#@register_snippet
class PersonTagViewSet(BaseSnippetViewSet):
    """
    Admin interface for managing Person Tags
    """
    model = PersonTag
    icon = "user"
    menu_label = _("Person Tags")
    menu_order = 320
    add_to_settings_menu = False

    # ======================
    # SEARCH & FILTERING
    # ======================
    search_fields = [
        "name",
        "description",
        "meta_title",
        "meta_description",
        "category__name",
    ]

    ordering = ["name"]
    list_per_page = 50

    # ======================
    # TABLE CONFIGURATION
    # ======================
    list_display = [
        "display_tag",
        "display_category",
        "display_color",
        "usage_count_display",
        "active_persons_display",
        "live_status_column",
        "updated_at_column",
    ]

    list_filter = [
        "category",
        "live",
        "category__is_public",
    ]

    list_export = [
        "name",
        "slug",
        "category",
        "color",
        "icon",
        "usage_count",
        "published_items_count",
        "meta_title",
        "meta_description",
        "live",
        "created_at",
        "updated_at",
    ]

    csv_filename = "person_tags_export.csv"

    # ======================
    # DISPLAY HELPERS
    # ======================

    @staticmethod
    def display_tag(obj):
        """Display tag with color and icon."""
        icon_html = f'<i class="{obj.icon}"></i> ' if obj.icon else ''
        color_style = f'style="color: {obj.color}"' if obj.color else ''

        url = reverse('persontags:edit', args=[obj.pk])
        return format_html(
            '<a href="{}" {}><strong>{} {}</strong></a>',
            url,
            color_style,
            icon_html,
            obj.name
        )
    display_tag.short_description = _("Tag")
    display_tag.admin_order_field = "name"

    @staticmethod
    def display_category(obj):
        """Display category with color."""
        if obj.category:
            color_style = f'style="color: {obj.category.color}"' if obj.category.color else ''
            return format_html(
                '<span {}>{}</span>',
                color_style,
                obj.category.name
            )
        return "—"
    display_category.short_description = _("Category")
    display_category.admin_order_field = "category"

    @staticmethod
    def display_color(obj):
        """Display color as a colored circle."""
        if obj.color:
            return format_html(
                '<div style="display: inline-block; width: 20px; height: 20px; '
                'background-color: {}; border-radius: 50%; border: 1px solid #ccc;" '
                'title="{}"></div>',
                obj.color,
                obj.color
            )
        return "—"
    display_color.short_description = _("Color")

    @staticmethod
    def usage_count_display(obj):
        """Display usage count with contextual color."""
        if obj.usage_count == 0:
            badge_class = "w-badge w-badge--critical"
        elif obj.usage_count < 5:
            badge_class = "w-badge w-badge--warning"
        else:
            badge_class = "w-badge w-badge--success"

        return format_html(
            '<span class="{}">{}</span>',
            badge_class,
            obj.usage_count
        )
    usage_count_display.short_description = _("Usage")
    usage_count_display.admin_order_field = "usage_count"

    @staticmethod
    def active_persons_display(obj):
        """Display active persons count."""
        count = obj.published_items_count
        url = reverse('persons:index') + f'?tags__id={obj.pk}'
        return format_html(
            '<a href="{}" class="persons-count-link">{}</a>',
            url,
            f"👥 {count}" if count > 0 else "—"
        )
    active_persons_display.short_description = _("Persons")

    # ======================
    # CUSTOM COLUMNS
    # ======================


#@register_snippet
class PersonTagCategoryViewSet(BaseSnippetViewSet):
    """
    Admin interface for managing Person Tag Categories
    """
    model = PersonTagCategory
    icon = "folder-inverse"
    menu_label = _("Person Tag Categories")
    menu_order = 321
    add_to_settings_menu = False

    # ======================
    # SEARCH & FILTERING
    # ======================
    search_fields = [
        "name",
        "slug",
        "description",
    ]

    ordering = ["display_order", "name"]
    list_per_page = 50

    # ======================
    # TABLE CONFIGURATION
    # ======================
    list_display = [
        "display_category",
        "display_color",
        "tag_count_display",
        "published_tag_count_display",
        "is_public_display",
        "live_status_column",
        "updated_at_column",
    ]

    list_filter = [
        "is_public",
        "live",
    ]

    list_export = [
        "name",
        "slug",
        "color",
        "icon",
        "display_order",
        "tag_count",
        "published_tag_count",
        "is_public",
        "live",
        "created_at",
        "updated_at",
    ]

    csv_filename = "person_tag_categories_export.csv"

    # ======================
    # DISPLAY HELPERS
    # ======================

    @staticmethod
    def display_category(obj):
        """Display category with color and icon."""
        icon_html = f'<i class="{obj.icon}"></i> ' if obj.icon else ''
        color_style = f'style="color: {obj.color}"' if obj.color else ''

        url = reverse('persontagcategories:edit', args=[obj.pk])
        return format_html(
            '<a href="{}" {}><strong>{} {}</strong></a>',
            url,
            color_style,
            icon_html,
            obj.name
        )
    display_category.short_description = _("Category")
    display_category.admin_order_field = "name"

    @staticmethod
    def display_color(obj):
        """Display color as a colored circle."""
        if obj.color:
            return format_html(
                '<div style="display: inline-block; width: 20px; height: 20px; '
                'background-color: {}; border-radius: 50%; border: 1px solid #ccc;" '
                'title="{}"></div>',
                obj.color,
                obj.color
            )
        return "—"
    display_color.short_description = _("Color")

    @staticmethod
    def tag_count_display(obj):
        """Display total tag count."""
        count = obj.tag_count
        url = reverse('persontags:index') + f'?category__id={obj.pk}'
        return format_html(
            '<a href="{}" class="tag-count-link">{}</a>',
            url,
            f"🏷️ {count}" if count > 0 else "—"
        )
    tag_count_display.short_description = _("Total Tags")

    @staticmethod
    def published_tag_count_display(obj):
        """Display published tag count."""
        count = obj.published_tag_count
        return format_html(
            '<span class="published-tag-count">{}</span>',
            f"✅ {count}" if count > 0 else "—"
        )
    published_tag_count_display.short_description = _("Published Tags")

    @staticmethod
    def is_public_display(obj):
        """Display public status."""
        if obj.is_public:
            return format_html(
                '<span class="w-badge w-badge--success">🌐 {}</span>',
                _("Public")
            )
        return format_html(
            '<span class="w-badge w-badge--critical">🔒 {}</span>',
            _("Private")
        )
    is_public_display.short_description = _("Visibility")
