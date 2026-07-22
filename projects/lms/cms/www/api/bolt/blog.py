"""
Bolt Blog API — detail, featured, related posts, categories.

Extends the existing bolt blog endpoints in ``apis.py`` (which provide
basic listing) with additional detail and discovery endpoints.
"""

from __future__ import annotations

import logging

from www.api.bolt.helpers import paginate_queryset, get_image_url, get_user_display_name

logger = logging.getLogger(__name__)


def register_handlers(bolt):
    """Register blog handlers on the given BoltAPI instance."""

    # ── GET /apis/blog/<pk> — single post detail ──
    @bolt.get("/blog/<int:pk>")
    def get_blog_post(request, pk):
        """GET /apis/blog/<pk> — Single blog post detail."""
        from www.content.models.blog import BlogPost

        try:
            post = BlogPost.objects.get(pk=pk, is_published=True)
        except BlogPost.DoesNotExist:
            return {"status": "error", "message": "Post not found"}, 404

        return {"status": "success", "data": _serialize_blog_post(post)}

    # ── GET /apis/blog/featured — featured/popular posts ──
    @bolt.get("/blog/featured")
    def list_featured_posts(request):
        """GET /apis/blog/featured — Top featured blog posts."""
        from www.content.models.blog import BlogPost

        posts = BlogPost.objects.filter(is_published=True).order_by("-published_at")[:3]
        data = [_serialize_blog_post(p) for p in posts]
        return {"status": "success", "count": len(data), "results": data}

    # ── GET /apis/blog/<pk>/related — related posts ──
    @bolt.get("/blog/<int:pk>/related")
    def list_related_posts(request, pk):
        """GET /apis/blog/<pk>/related — Related posts (same category, max 3)."""
        from www.content.models.blog import BlogPost

        try:
            post = BlogPost.objects.get(pk=pk, is_published=True)
        except BlogPost.DoesNotExist:
            return {"status": "error", "message": "Post not found"}, 404

        # Try to find related posts by category
        related_qs = BlogPost.objects.filter(is_published=True).exclude(pk=pk)

        if post.category and isinstance(post.category, dict) and post.category.get("name"):
            related_qs = related_qs.filter(category__name=post.category["name"])

        related = related_qs.order_by("-published_at")[:3]
        data = [_serialize_blog_post(p) for p in related]
        return {"status": "success", "data": data}

    # ── GET /apis/blog/categories — blog categories ──
    @bolt.get("/blog/categories")
    def list_blog_categories(request):
        """GET /apis/blog/categories — Blog categories with post counts."""
        try:
            from plugins.blog.models.category import BlogCategory
            categories = BlogCategory.objects.all().order_by("name")
        except Exception:
            # Fall back to distinct category values from blog posts
            from www.content.models.blog import BlogPost
            cats = BlogPost.objects.filter(is_published=True).values_list("category", flat=True).distinct()
            seen = set()
            data = []
            for c in cats:
                if c and isinstance(c, dict):
                    name = c.get("name", "")
                    if name and name not in seen:
                        seen.add(name)
                        data.append({
                            "id": 0,
                            "name": name,
                            "slug": c.get("slug", ""),
                            "post_count": BlogPost.objects.filter(category__name=name, is_published=True).count(),
                        })
            return {"status": "success", "count": len(data), "results": data}

        data = [
            {
                "id": c.pk,
                "name": c.name,
                "slug": getattr(c, "slug", ""),
                "post_count": c.posts.filter(status="published").count() if hasattr(c, "posts") else 0,
            }
            for c in categories
        ]
        return {"status": "success", "count": len(data), "results": data}


# ═══════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════


def _serialize_blog_post(post) -> dict:
    """Serialize a BlogPost into a response shape matching DRF BlogPostListSerializer."""
    # Extract category info
    category_name = ""
    category_id = None
    raw_cat = post.category if hasattr(post, "category") else None
    if raw_cat:
        if isinstance(raw_cat, dict):
            category_name = raw_cat.get("name", "")
            category_id = raw_cat.get("id", None)
        elif isinstance(raw_cat, str):
            category_name = raw_cat

    # Tags
    tags = []
    try:
        tags = list(post.tags.values_list("name", flat=True))
    except Exception:
        pass

    # Featured image
    image_url = get_image_url(post.featured_image) if hasattr(post, "featured_image") else ""

    return {
        "id": post.pk,
        "title": post.title,
        "slug": getattr(post, "slug", ""),
        "excerpt": getattr(post, "excerpt", ""),
        "content": getattr(post, "content", ""),
        "author": getattr(post, "author", ""),
        "author_name": getattr(post, "author", ""),
        "author_avatar": "",
        "category": category_id,
        "category_name": category_name,
        "tags": tags,
        "featured_image": image_url,
        "is_published": post.is_published,
        "view_count": 0,
        "published_at": post.published_at.isoformat() if hasattr(post, "published_at") and post.published_at else None,
        "created_at": post.created_at.isoformat() if hasattr(post, "created_at") and post.created_at else None,
        "updated_at": post.updated_at.isoformat() if hasattr(post, "updated_at") and post.updated_at else None,
    }
