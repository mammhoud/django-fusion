"""Django REST views for Fusion CMS blog API.

Mount: /api/blog, /api/blog/<slug>, /api/blog/categories, /api/blog/tags
"""

from __future__ import annotations

import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)


def _qp(request, key: str, default: str = "") -> str:
    return request.GET.get(key, default)


def _qp_int(request, key: str, default: int = 1) -> int:
    try:
        return int(_qp(request, key, str(default)))
    except (TypeError, ValueError):
        return default


def list_blog_posts(request):
    """GET /api/blog — Blog post listing with pagination, search, and filters."""
    try:
        from apps.pages.blog.models.post import BlogPost

        qs = BlogPost.objects.filter(status="published").order_by("-published_date")

        q = _qp(request, "q")
        if q:
            qs = qs.filter(title__icontains=q)
        cat = _qp(request, "category")
        if cat:
            qs = qs.filter(categories__slug=cat)
        tag = _qp(request, "tag")
        if tag:
            qs = qs.filter(tags__slug=tag)

        page = _qp_int(request, "page", 1)
        per_page = _qp_int(request, "per_page", 12)
        total = qs.count()
        posts = qs[(page - 1) * per_page : page * per_page]

        return JsonResponse({
            "data": [
                {
                    "id": p.pk, "title": p.title, "slug": p.slug,
                    "excerpt": p.excerpt,
                    "author": p.author.get_full_name() if p.author else "",
                    "published_date": p.published_date.isoformat() if p.published_date else None,
                    "featured_image_url": (
                        p.featured_image.get_rendition("fill-800x400").url
                        if p.featured_image else None
                    ),
                    "categories": [{"slug": c.slug, "name": c.name} for c in p.categories.all()],
                    "tags": [{"slug": t.slug, "name": t.name} for t in p.tags.all()],
                    "reading_time": p.get_reading_time() if hasattr(p, "get_reading_time") else 5,
                }
                for p in posts
            ],
            "pagination": {
                "page": page, "per_page": per_page, "total": total,
                "total_pages": max(1, (total + per_page - 1) // per_page),
            },
        })
    except Exception:
        logger.exception("Error listing blog posts")
        return JsonResponse(
            {"data": [], "pagination": {"page": 1, "per_page": 12, "total": 0, "total_pages": 0}}
        )


def blog_post_detail(request, slug):
    """GET /api/blog/<slug> — Single blog post detail with related posts."""
    try:
        from apps.pages.blog.models.post import BlogPost

        post = BlogPost.objects.filter(slug=slug, status="published").first()
        if post is None:
            return JsonResponse({"status": "error", "message": "Post not found"}, status=404)

        try:
            related_qs = post.get_related_posts(limit=3)
            related = [
                {
                    "title": rp.title, "slug": getattr(rp, "slug", ""),
                    "excerpt": getattr(rp, "excerpt", ""),
                    "featured_image_url": (
                        rp.featured_image.get_rendition("fill-400x200").url
                        if rp.featured_image else None
                    ),
                }
                for rp in related_qs
            ]
        except Exception:
            related = []

        return JsonResponse({
            "id": post.pk, "title": post.title, "slug": post.slug,
            "content": post.content, "excerpt": post.excerpt,
            "author": {
                "name": post.author.get_full_name() if post.author else "",
                "id": post.author.pk if post.author else None,
            },
            "published_date": post.published_date.isoformat() if post.published_date else None,
            "featured_image_url": (
                post.featured_image.get_rendition("fill-1200x600").url
                if post.featured_image else None
            ),
            "categories": [{"slug": c.slug, "name": c.name} for c in post.categories.all()],
            "tags": [{"slug": t.slug, "name": t.name} for t in post.tags.all()],
            "reading_time": post.get_reading_time() if hasattr(post, "get_reading_time") else 5,
            "likes_count": getattr(post, "likes_count", 0),
            "meta_description": getattr(post, "meta_description", ""),
            "related_posts": related,
        })
    except Exception:
        logger.exception("Error loading blog post")
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)


def blog_categories(request):
    """GET /api/blog/categories — List all blog categories with post counts."""
    try:
        from django.db import models
        from django.db.models import Count
        from apps.pages.blog.models.category import BlogCategory

        cats = BlogCategory.objects.annotate(
            post_count=Count("posts", filter=models.Q(posts__status="published"))
        ).filter(post_count__gt=0).order_by("name")
        return JsonResponse({
            "categories": [{"slug": c.slug, "name": c.name, "post_count": c.post_count} for c in cats],
        })
    except Exception:
        return JsonResponse({"categories": []})


def blog_tags(request):
    """GET /api/blog/tags — List all blog tags with post counts."""
    try:
        from django.db import models
        from django.db.models import Count
        from apps.pages.blog.models.tag import BlogTag

        tags = BlogTag.objects.annotate(
            post_count=Count("posts", filter=models.Q(posts__status="published"))
        ).filter(post_count__gt=0).order_by("-post_count")[:50]
        return JsonResponse({
            "tags": [{"slug": t.slug, "name": t.name, "post_count": t.post_count} for t in tags],
        })
    except Exception:
        return JsonResponse({"tags": []})
