"""
Services for blog tag operations.

TagService and PostFilterService are thin subclasses of the reusable
base classes provided by django-osoul.  All core logic lives in
django_osoul.services.tagging so it can be reused across apps.
"""

from django.db.models import Count, Q
from django_osoul.services import PostFilterServiceBase, TagServiceBase

from .models import BlogPost, BlogTag


class TagService(TagServiceBase):
    """Tag service for the blog app."""

    post_model = BlogPost
    tag_model = BlogTag
    tag_related_name = "posts"


class PostFilterService(PostFilterServiceBase):
    """Post filter service for the blog app."""

    tag_field = "tags__slug"
    category_field = "categories__slug"
    search_fields = ["title", "content", "excerpt"]
