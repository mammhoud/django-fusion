"""
django_fusion.services.tagging
==============================

Reusable tag and post-filter service classes.

These services are generic and work with any Django model that has a
ManyToMany ``tags`` field (using django-taggit or a compatible slug-based
tag model) and an optional ``categories`` ManyToMany field.

Classes
-------
TagServiceBase
    Generic tag operations: popular tags, related tags, tag cloud, merge,
    cleanup.  Subclass and set ``post_model`` and ``tag_model`` to use.

PostFilterServiceBase
    Generic queryset filtering by tags, categories, status, and free-text
    search.  Subclass and override ``tag_field`` / ``category_field`` if
    your model uses different related-field names.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Optional

from django.db.models import Count, Q, QuerySet


class TagServiceBase:
    """
    Generic service for tag-related operations.

    Subclass and set class attributes::

        class BlogTagService(TagServiceBase):
            post_model = BlogPost
            tag_model = BlogTag
            tag_related_name = "posts"   # reverse accessor on tag → posts

    All methods are ``@staticmethod``-style but use ``cls`` so subclasses
    can override ``post_model`` / ``tag_model`` without passing them
    explicitly.
    """

    post_model: Any = None
    tag_model: Any = None
    tag_related_name: str = "posts"

    # ------------------------------------------------------------------
    # Class-level helpers
    # ------------------------------------------------------------------

    @classmethod
    def _posts(cls) -> QuerySet:
        if cls.post_model is None:
            raise NotImplementedError("Set post_model on the subclass.")
        return cls.post_model.objects.all()

    @classmethod
    def _tags(cls) -> QuerySet:
        if cls.tag_model is None:
            raise NotImplementedError("Set tag_model on the subclass.")
        return cls.tag_model.objects.all()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def get_popular_tags(cls, limit: int = 10) -> QuerySet:
        """Return the *limit* most-used tags (with at least one post)."""
        return (
            cls._tags()
            .annotate(post_count=Count(cls.tag_related_name))
            .filter(post_count__gt=0)
            .order_by("-post_count")[:limit]
        )

    @classmethod
    def get_related_tags(cls, tag: Any, limit: int = 5) -> QuerySet:
        """Return tags that co-occur with *tag* in the same posts."""
        posts = cls._posts().filter(tags=tag)
        return (
            cls._tags()
            .filter(**{f"{cls.tag_related_name}__in": posts})
            .exclude(id=tag.id)
            .annotate(post_count=Count(cls.tag_related_name))
            .order_by("-post_count")[:limit]
        )

    @classmethod
    def search_tags(cls, query: str) -> QuerySet:
        """Return tags whose name or slug contains *query* (case-insensitive)."""
        return cls._tags().filter(
            Q(name__icontains=query) | Q(slug__icontains=query)
        ).order_by("name")

    @classmethod
    def get_tag_cloud(cls, limit: int = 30) -> List[Any]:
        """
        Return tags with a ``size`` attribute (1–5) for tag-cloud rendering.

        Tags are sorted alphabetically.
        """
        tags = list(
            cls._tags()
            .annotate(post_count=Count(cls.tag_related_name))
            .filter(post_count__gt=0)
            .order_by("-post_count")[:limit]
        )
        if not tags:
            return []

        counts = [t.post_count for t in tags]
        min_count, max_count = min(counts), max(counts)

        for tag in tags:
            if max_count == min_count:
                tag.size = 3
            else:
                tag.size = 1 + int(
                    (tag.post_count - min_count) / (max_count - min_count) * 4
                )

        return sorted(tags, key=lambda t: t.name)

    @classmethod
    def merge_tags(cls, old_tag: Any, new_tag: Any) -> None:
        """Move all posts from *old_tag* to *new_tag*, then delete *old_tag*."""
        for post in cls._posts().filter(tags=old_tag):
            post.tags.add(new_tag)
            post.tags.remove(old_tag)
        old_tag.delete()

    @classmethod
    def cleanup_unused_tags(cls) -> int:
        """Delete tags with no posts and return the count removed."""
        unused = (
            cls._tags()
            .annotate(post_count=Count(cls.tag_related_name))
            .filter(post_count=0)
        )
        count = unused.count()
        unused.delete()
        return count


class PostFilterServiceBase:
    """
    Generic queryset filtering for post-like models.

    Subclass and override class attributes as needed::

        class BlogPostFilterService(PostFilterServiceBase):
            tag_field = "tags__slug"
            category_field = "categories__slug"
            search_fields = ["title", "content", "excerpt"]

    All methods accept and return a ``QuerySet`` so they can be chained.
    """

    tag_field: str = "tags__slug"
    category_field: str = "categories__slug"
    search_fields: List[str] = ["title", "content", "excerpt"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def filter_by_tags(
        cls,
        queryset: QuerySet,
        tag_slugs: Iterable[str],
        match_all: bool = False,
    ) -> QuerySet:
        """
        Filter *queryset* by tag slugs.

        Args:
            queryset: Base queryset.
            tag_slugs: Iterable of tag slug strings.
            match_all: If ``True``, posts must have **all** tags; otherwise
                posts with **any** of the tags are returned.

        Returns:
            Filtered queryset (distinct).
        """
        slugs = list(tag_slugs)
        if not slugs:
            return queryset

        if match_all:
            for slug in slugs:
                queryset = queryset.filter(**{cls.tag_field: slug})
        else:
            queryset = queryset.filter(**{f"{cls.tag_field}__in": slugs})

        return queryset.distinct()

    @classmethod
    def filter_by_categories(
        cls,
        queryset: QuerySet,
        category_slugs: Iterable[str],
    ) -> QuerySet:
        """Filter *queryset* to posts in any of the given category slugs."""
        slugs = list(category_slugs)
        if not slugs:
            return queryset
        return queryset.filter(
            **{f"{cls.category_field}__in": slugs}
        ).distinct()

    @classmethod
    def filter_by_status(
        cls,
        queryset: QuerySet,
        status: Optional[str],
    ) -> QuerySet:
        """Filter *queryset* by ``status`` field value."""
        if not status:
            return queryset
        return queryset.filter(status=status)

    @classmethod
    def search_posts(
        cls,
        queryset: QuerySet,
        query: str,
    ) -> QuerySet:
        """
        Full-text search across :attr:`search_fields` (OR-combined icontains).
        """
        if not query:
            return queryset

        q_filter = Q()
        for field in cls.search_fields:
            lookup = field if "__" in field else f"{field}__icontains"
            q_filter |= Q(**{lookup: query})

        return queryset.filter(q_filter)

    @classmethod
    def apply_filters(
        cls,
        queryset: QuerySet,
        tags: Optional[Iterable[str]] = None,
        categories: Optional[Iterable[str]] = None,
        status: Optional[str] = None,
        query: Optional[str] = None,
    ) -> QuerySet:
        """Apply all filters in sequence and return the result."""
        queryset = cls.filter_by_tags(queryset, tags or [])
        queryset = cls.filter_by_categories(queryset, categories or [])
        queryset = cls.filter_by_status(queryset, status)
        queryset = cls.search_posts(queryset, query or "")
        return queryset
