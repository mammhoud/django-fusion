"""
Wagtail hooks for Blog application.
"""
from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import BlogCategory, BlogPost, BlogTag


class BlogCategoryViewSet(SnippetViewSet):
    model = BlogCategory
    icon = "folder"
    list_display = ["name", "slug", "get_post_count"]
    search_fields = ["name"]


class BlogTagViewSet(SnippetViewSet):
    model = BlogTag
    icon = "tag"
    list_display = ["name", "slug", "get_post_count"]
    search_fields = ["name"]


class BlogPostViewSet(SnippetViewSet):
    model = BlogPost
    icon = "doc-full"
    list_display = ["title", "author", "status", "published_date"]
    list_filter = ["status", "categories"]
    search_fields = ["title", "content"]


class BlogSnippetGroup(SnippetViewSetGroup):
    menu_label = _("Blog Snippets")
    menu_icon = "doc-full"
    menu_order = 160
    items = (
        BlogCategoryViewSet,
        BlogTagViewSet,
        BlogPostViewSet,
    )


register_snippet(BlogSnippetGroup)
