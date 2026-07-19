"""
Services for blog tag operations.

TagService and PostFilterService are thin subclasses of the reusable
base classes provided by django-fusion.  All core logic lives in
django_fusion.services.tagging so it can be reused across apps.
"""

from django.db.models import Count, Q
from django_fusion.core.services import PostFilterServiceBase, TagServiceBase

from .models import BlogPost, BlogTag


class TagService(TagServiceBase):
    """
    Tag service for the blog app.

    Delegates to django_fusion.services.TagServiceBase
    """

    post_model = BlogPost
    tag_model = BlogTag
    tag_related_name = "posts"


class PostFilterService(PostFilterServiceBase):
    """
    Post filter service for the blog app.

    Delegates to django_fusion.services.PostFilterServiceBase
    """

    tag_field = "tags__slug"
    category_field = "categories__slug"
    search_fields = ["title", "content", "excerpt"]
