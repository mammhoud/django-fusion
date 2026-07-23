"""
Blog API — posts list, detail, categories, featured (bolt-pattern adapter).

Matches the RTK Query slice at: store/api/endpoints/blog.ts
"""

import logging

from django.db.models import Q
from django.shortcuts import get_object_or_404

from plugins.blog.models import BlogPost, BlogCategory
from www.api.data_adapter import (
    bolt_view,
    paginate_queryset,
    parse_body,
    get_image_url,
    get_user_display_name,
    paginated_response,
)

logger = logging.getLogger(__name__)


def _serialize_post(post: BlogPost) -> dict:
    """Serialize a BlogPost to the frontend-expected format."""
    image_url = get_image_url(getattr(post, "featured_image", None))

    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "excerpt": post.excerpt or "",
        "content": str(post.content) if post.content else "",
        "featured_image": image_url,
        "author": post.author_id,
        "author_name": get_user_display_name(post.author),
        "author_avatar": "",
        "category": post.categories.first().id if post.categories.exists() else None,
        "category_name": (
            post.categories.first().name
            if post.categories.exists()
            else "Uncategorized"
        ),
        "categories": list(post.categories.values_list("name", flat=True)),
        "tags": list(post.tags.values_list("name", flat=True)),
        "reading_time": post.get_reading_time(),
        "status": post.status,
        "is_published": post.is_published,
        "published_date": (
            post.published_date.isoformat() if post.published_date else None
        ),
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        "likes_count": post.likes_count,
    }


def _serialize_category(cat: BlogCategory) -> dict:
    """Serialize a BlogCategory."""
    return {
        "id": cat.id,
        "name": cat.name,
        "slug": cat.slug,
        "description": cat.description or "",
        "post_count": cat.posts.filter(status="published").count(),
    }


# ── Blog Post List ──


@bolt_view
def blog_post_list(request):
    """GET /api/blog/posts/ — List published blog posts."""
    queryset = BlogPost.objects.filter(status="published").order_by("-published_date")

    q = request.GET.get("search", "").strip()
    if q:
        queryset = queryset.filter(Q(title__icontains=q) | Q(excerpt__icontains=q))

    category = request.GET.get("category", "").strip()
    if category:
        queryset = queryset.filter(categories__slug=category)

    tag = request.GET.get("tag", "").strip()
    if tag:
        queryset = queryset.filter(tags__name__iexact=tag)

    featured = request.GET.get("featured", "").strip()
    if featured == "true":
        queryset = queryset.order_by("-likes_count", "-published_date")[:3]

    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 10))
    items, pagination = paginate_queryset(queryset, request, page_size)

    return paginated_response(
        items, pagination, request, [_serialize_post(p) for p in items]
    )


# ── Blog Post Detail ──


@bolt_view
def blog_post_detail(request, pk):
    """GET /api/blog/posts/<pk>/ — Get single blog post details."""
    post = get_object_or_404(BlogPost, pk=pk, status="published")
    data = _serialize_post(post)
    data["related_posts"] = [
        _serialize_post(p) for p in post.get_related_posts(limit=3)
    ]
    return {"status": "success", "data": data}


# ── Featured Posts ──


@bolt_view
def featured_posts(request):
    """GET /api/blog/posts/featured/ — Get featured/popular blog posts."""
    posts = BlogPost.objects.filter(status="published").order_by(
        "-likes_count", "-published_date"
    )[:3]
    return {
        "results": [_serialize_post(p) for p in posts],
        "count": posts.count(),
        "next": None,
        "previous": None,
    }


# ── Blog Categories ──


@bolt_view
def blog_category_list(request):
    """GET /api/blog/categories/ — List blog categories with post counts."""
    categories = BlogCategory.objects.all().order_by("name")
    return {
        "results": [_serialize_category(c) for c in categories],
        "count": categories.count(),
        "next": None,
        "previous": None,
    }
