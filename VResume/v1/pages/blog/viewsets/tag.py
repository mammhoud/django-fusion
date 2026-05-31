"""
Blog Tag Snippet ViewSet
Manages tags for blog posts and snippets
"""
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn

from core.snippets import BaseSnippetViewSet
from pages.blog.models import BlogTag


class BlogTagViewSet(BaseSnippetViewSet):
    """
    Blog Tag Snippet ViewSet
    Manages tags for blog posts and snippets
    
    Features:
    - Color coding for visual distinction
    - Icon support (Bootstrap icons)
    - Description field for context
    - Active/inactive status
    - Full search indexing
    
    Menu: Blog > Tags
    """
    model = BlogTag
    icon = "tag"
    menu_label = _("Blog Tags")
    menu_name = "blog_tags"
    menu_group = "blog"
    menu_order = 100

    list_display = [
        "name",
        "slug",
        BooleanColumn("is_active", label=_("Active")),
    ]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["name"]
