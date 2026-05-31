"""
Blog Post Snippet ViewSet
Manages reusable blog post snippets
"""
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn

from core.snippets import BaseSnippetViewSet
from pages.blog.models import BlogPost


class BlogPostViewSet(BaseSnippetViewSet):
    """
    Blog Post Snippet ViewSet
    Manages reusable blog post snippets
    
    Features:
    - Rich text content with StreamField
    - Multiple author support
    - Enhanced tagging system
    - SEO fields
    - Analytics tracking
    - Featured post designation
    
    Menu: Blog > Posts
    """
    model = BlogPost
    icon = "doc-full"
    menu_label = _("Blog Posts")
    menu_name = "blog_posts"
    menu_group = "blog"
    menu_order = 130

    list_display = [
        "title",
        BooleanColumn("is_published", label=_("Published")),
        "page_views",
    ]
    list_filter = ["is_published", "published_date"]
    search_fields = ["title", "subtitle", "introduction", "body"]
    ordering = ["-created_at"]
