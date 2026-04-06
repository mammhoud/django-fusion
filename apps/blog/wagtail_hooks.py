"""
Wagtail hooks for Blog application.
"""
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

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


register_snippet(BlogCategoryViewSet)
register_snippet(BlogTagViewSet)
register_snippet(BlogPostViewSet)
