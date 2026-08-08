"""
Legacy blog model shim.

The canonical blog implementation lives in ``apps.pages.blog.models``
(BlogPost, BlogIndexPage, BlogTag, BlogCategory, BlogComment). This package
previously defined a duplicate Wagtail-page-based blog (BlogPage,
BlogIndexPage, BlogPageTag) that clashed with the canonical models when
imported during test discovery and produced fields.E304/E305 reverse
accessor errors.

It is now a thin re-export shim so any legacy import path continues to
resolve, without registering any additional models.
"""
from apps.pages.blog.models import (  # noqa: F401
    BlogCategory,
    BlogComment,
    BlogIndexPage,
    BlogPost,
    BlogTag,
)

# Backwards-compatible aliases for the legacy names (best-effort mapping).
BlogPage = BlogIndexPage  # noqa: F401 — legacy page alias
BlogPageTag = BlogTag  # noqa: F401 — legacy through alias

__all__ = [
    "BlogCategory",
    "BlogComment",
    "BlogIndexPage",
    "BlogPost",
    "BlogTag",
    "BlogPage",
    "BlogPageTag",
]
