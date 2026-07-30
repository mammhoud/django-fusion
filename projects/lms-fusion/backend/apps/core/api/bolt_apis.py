"""
Fusion LMS — django-bolt API server.

High-performance REST API with Rust-backed request handling (via runbolt).
Provides endpoints for pages, health, branding, and LMS-specific data.

Mount URL: path("api/", bolt.urls)

Schema: Uses dict-based responses (bolt_view adapter pattern)
plus FusionCodec encoding for fragment rendering compatibility.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# Try to import real BoltAPI; fall back gracefully if not available
try:
    from django_bolt import BoltAPI

    bolt = BoltAPI(
        prefix="/api",
        namespace="lms-fusion-bolt",
        title="Fusion LMS API",
        version="1.0.0",
        description="High-performance API for Fusion LMS — serves Next.js frontend",
    )

    # Register FUSION_ASSETS endpoints for OpenAPI schema
    from django_fusion.plugins.bolt.api import register_fusion_assets_bolt
    register_fusion_assets_bolt(bolt)

    _has_bolt = True
except ImportError:
    _has_bolt = False
    bolt = None
    logger.warning(
        "django_bolt not installed — bolt API endpoints unavailable. "
        "Install django-bolt for high-performance API support."
    )


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════

def _qp(request, key: str, default: str = "") -> str:
    """Get a query parameter from a request."""
    if hasattr(request, "query"):
        return request.query.get(key, default)
    if hasattr(request, "GET"):
        return request.GET.get(key, default)
    return default


def _qp_int(request, key: str, default: int = 1) -> int:
    """Get an integer query parameter safely."""
    try:
        return int(_qp(request, key, str(default)))
    except (TypeError, ValueError):
        return default


# ═══════════════════════════════════════════════════════════════════════
# Health endpoint
# ═══════════════════════════════════════════════════════════════════════

if _has_bolt and bolt is not None:

    @bolt.get("/health")
    def health_check(request):
        """GET /api/health — Health check with fusion status."""
        from django_fusion.routes import FusionSessionChecker

        checker = FusionSessionChecker()
        preference = checker.get_preference(request)
        return {
            "status": "ok",
            "service": "lms-fusion-bolt",
            "fusion_render_first": preference,
            "has_bolt": True,
        }

    # ═══════════════════════════════════════════════════════════════════
    # Pages API
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/pages/<slug>")
    def page_detail(request, slug):
        """GET /api/pages/<slug> — Return public page content."""
        from apps.pages.pages.content import STATIC_PAGES, normalize_slug

        normalized = normalize_slug(slug)
        page = STATIC_PAGES.get(normalized)
        if page is None:
            return {"status": "error", "message": "Page not found"}, 404
        return page

    @bolt.get("/pages/<slug>/fragment")
    def page_fragment_pointer(request, slug):
        """GET /api/pages/<slug>/fragment — Fragment pointer with fusion metadata."""
        from apps.pages.pages.content import STATIC_PAGES, normalize_slug
        from apps.core.api.data_adapter import fusion_response
        from django_fusion.routes import fusion_json_response

        normalized = normalize_slug(slug)
        if normalized not in STATIC_PAGES:
            return fusion_json_response({"error": "Page not found"}, status=404)

        fragment_name = f"pages.{normalized.replace('-', '_')}"
        pointer = fusion_response(
            fragment_name,
            request,
            extra={
                "page_slug": normalized,
                "title": STATIC_PAGES[normalized]["title"],
            },
        )
        return fusion_json_response(data=pointer, status=200)

    # ═══════════════════════════════════════════════════════════════════
    # Branding (mounted via api/urls.py → fusion_branding.py)
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/fusion/branding")
    def branding(request):
        """GET /api/fusion/branding — Dynamic site branding.

        NOTE: This bolt-registered route is superseded by the standalone
        ``fusion_branding.py`` view mounted directly in ``apps.core.api.urls``.
        The standalone view is the canonical source; this bolt version exists
        only for backward compatibility if bolt.urls is ever mounted separately."""
        try:
            from apps.pages.branding.context_processors import fusion_branding_context

            ctx = fusion_branding_context(request)
            return ctx.get("fusion_branding", {})
        except Exception:
            return {
                "site_name": os.environ.get("FUSION_SITE_NAME", "Fusion LMS"),
                "company_name": os.environ.get("FUSION_COMPANY_NAME", "Fusion Inc."),
                "creator_name": os.environ.get("FUSION_CREATOR_NAME", "Fusion Team"),
                "primary_color": os.environ.get("FUSION_PRIMARY_COLOR", "#00a1b3"),
            }

    # ═══════════════════════════════════════════════════════════════════
    # Fusion health
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/fusion/health")
    def fusion_health(request):
        """GET /api/fusion/health — Fusion rendering preference."""
        from django_fusion.routes import FusionSessionChecker

        was_cached = "fusion_render_first" in getattr(request, "session", {})
        checker = FusionSessionChecker()
        preference = checker.get_preference(request)

        ua = (getattr(request, "META", {}).get("HTTP_USER_AGENT") or "").lower()[:60]

        return {
            "status": 200,
            "message": "Success",
            "data": {
                "fusion_render_first": preference,
                "reason": f"user_agent: {ua}",
                "session_cached": was_cached,
            },
        }

    # ═══════════════════════════════════════════════════════════════════
    # Fusion Layouts
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/fusion/layouts")
    def fusion_layouts(request):
        """GET /api/fusion/layouts — Available layout options for FusionLayout.tsx."""
        from django.conf import settings
        layouts = getattr(settings, "FUSION_LAYOUTS", {
            "default": "Default",
            "full_width": "Full Width",
            "sidebar": "Sidebar",
            "blank": "Blank",
        })
        return {
            "layouts": [
                {"id": k, "name": v.title() if isinstance(v, str) else v}
                for k, v in layouts.items()
            ],
            "default": getattr(settings, "FUSION_DEFAULT_LAYOUT", "default"),
        }

    # ═══════════════════════════════════════════════════════════════════
    # Courses / LMS
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/courses")
    def list_courses(request):
        """GET /api/courses — Course catalog with search, filters, pagination."""
        try:
            from django.db import models
            from apps.pages.lms.models import Course

            qs = Course.objects.filter(is_published=True, is_active=True).order_by(
                "-is_featured", "-created_at"
            )

            q = _qp(request, "q")
            if q:
                qs = qs.filter(
                    models.Q(title__icontains=q)
                    | models.Q(short_description__icontains=q)
                )

            lang = _qp(request, "language")
            if lang:
                qs = qs.filter(language=lang)
            diff = _qp(request, "difficulty")
            if diff:
                qs = qs.filter(difficulty_level=diff)
            featured = _qp(request, "featured")
            if featured == "true":
                qs = qs.filter(is_featured=True)

            page = _qp_int(request, "page", 1)
            per_page = _qp_int(request, "per_page", 12)
            total = qs.count()
            courses = qs[(page - 1) * per_page : page * per_page]

            return {
                "data": [
                    {
                        "id": c.pk, "title": c.title, "slug": c.slug,
                        "short_description": getattr(c, "short_description", ""),
                        "image_url": c.image.file.url if getattr(c, "image", None) else None,
                        "instructor": c.instructor.get_full_name() if getattr(c, "instructor", None) else "",
                        "price": float(getattr(c, "current_price", 0)),
                        "original_price": float(getattr(c, "original_price", 0)) or None,
                        "difficulty": getattr(c, "difficulty_level", ""),
                        "language": getattr(c, "language", ""),
                        "duration": getattr(c, "duration", 0),
                        "rating": float(getattr(c, "average_rating", 0)),
                        "reviews_count": getattr(c, "reviews_count", 0),
                        "is_featured": getattr(c, "is_featured", False),
                        "has_certificate": getattr(c, "has_certificate", False),
                    }
                    for c in courses
                ],
                "pagination": {
                    "page": page, "per_page": per_page, "total": total,
                    "total_pages": max(1, (total + per_page - 1) // per_page),
                },
            }
        except Exception:
            return {
                "data": [],
                "pagination": {"page": 1, "per_page": 12, "total": 0, "total_pages": 0},
            }

    @bolt.get("/courses/<slug>")
    def course_detail(request, slug):
        """GET /api/courses/<slug> — Single course detail with modules."""
        try:
            from apps.pages.lms.models import Course

            course = Course.objects.filter(slug=slug, is_published=True, is_active=True).first()
            if course is None:
                return {"status": "error", "message": "Course not found"}, 404

            modules_data = []
            try:
                for mod in course.modules.filter(is_published=True).order_by("order"):
                    lessons = [
                        {"id": ln.pk, "title": ln.title, "is_preview": getattr(ln, "is_preview", False)}
                        for ln in mod.lessons.filter(is_published=True).order_by("order")
                    ]
                    modules_data.append({"id": mod.pk, "title": mod.title, "lessons": lessons})
            except Exception:
                pass

            return {
                "id": course.pk, "title": course.title, "slug": course.slug,
                "description": getattr(course, "description", ""),
                "short_description": getattr(course, "short_description", ""),
                "image_url": course.image.file.url if getattr(course, "image", None) else None,
                "instructor": {
                    "name": course.instructor.get_full_name() if getattr(course, "instructor", None) else "",
                },
                "price": float(getattr(course, "current_price", 0)),
                "original_price": float(getattr(course, "original_price", 0)) or None,
                "difficulty": getattr(course, "difficulty_level", ""),
                "language": getattr(course, "language", ""),
                "duration": getattr(course, "duration", 0),
                "rating": float(getattr(course, "average_rating", 0)),
                "reviews_count": getattr(course, "reviews_count", 0),
                "is_featured": getattr(course, "is_featured", False),
                "has_certificate": getattr(course, "has_certificate", False),
                "modules": modules_data,
            }
        except Exception:
            return {"status": "error", "message": "Internal server error"}, 500

    @bolt.get("/courses/filters")
    def course_filters(request):
        """GET /api/courses/filters — Available filter options for the course catalog."""
        try:
            from apps.pages.lms.models import Course

            languages = list(
                Course.objects.filter(is_published=True, is_active=True)
                .values_list("language", flat=True).distinct().order_by("language")
            )
            difficulties = list(
                Course.objects.filter(is_published=True, is_active=True)
                .values_list("difficulty_level", flat=True).distinct()
            )
            return {"languages": [l for l in languages if l], "difficulties": [d for d in difficulties if d]}
        except Exception:
            return {"languages": [], "difficulties": []}

    # ═══════════════════════════════════════════════════════════════════
    # Blog
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/blog")
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

            return {
                "data": [
                    {
                        "id": p.pk, "title": p.title, "slug": p.slug,
                        "excerpt": p.excerpt,
                        "author": p.author.get_full_name() if p.author else "",
                        "published_date": p.published_date.isoformat() if p.published_date else None,
                        "featured_image_url": p.featured_image.get_rendition("fill-800x400").url if p.featured_image else None,
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
            }
        except Exception:
            return {"data": [], "pagination": {"page": 1, "per_page": 12, "total": 0, "total_pages": 0}}

    @bolt.get("/blog/<slug>")
    def blog_post_detail(request, slug):
        """GET /api/blog/<slug> — Single blog post detail."""
        try:
            from apps.pages.blog.models.post import BlogPost

            post = BlogPost.objects.filter(slug=slug, status="published").first()
            if post is None:
                return {"status": "error", "message": "Post not found"}, 404

            return {
                "id": post.pk, "title": post.title, "slug": post.slug,
                "content": post.content, "excerpt": post.excerpt,
                "author": {"name": post.author.get_full_name() if post.author else "", "id": post.author.pk if post.author else None},
                "published_date": post.published_date.isoformat() if post.published_date else None,
                "featured_image_url": post.featured_image.get_rendition("fill-1200x600").url if post.featured_image else None,
                "categories": [{"slug": c.slug, "name": c.name} for c in post.categories.all()],
                "tags": [{"slug": t.slug, "name": t.name} for t in post.tags.all()],
                "reading_time": post.get_reading_time() if hasattr(post, "get_reading_time") else 5,
                "meta_description": post.meta_description if hasattr(post, "meta_description") else "",
            }
        except Exception:
            return {"status": "error", "message": "Internal server error"}, 500

    @bolt.get("/blog/categories")
    def blog_categories(request):
        """GET /api/blog/categories — List all blog categories with post counts."""
        try:
            from django.db import models
            from django.db.models import Count
            from apps.pages.blog.models.category import BlogCategory

            cats = BlogCategory.objects.annotate(
                post_count=Count("posts", filter=models.Q(posts__status="published"))
            ).filter(post_count__gt=0).order_by("name")
            return {"categories": [{"slug": c.slug, "name": c.name, "post_count": c.post_count} for c in cats]}
        except Exception:
            return {"categories": []}

    @bolt.get("/blog/tags")
    def blog_tags(request):
        """GET /api/blog/tags — List all blog tags with post counts."""
        try:
            from django.db import models
            from django.db.models import Count
            from apps.pages.blog.models.tag import BlogTag

            tags = BlogTag.objects.annotate(
                post_count=Count("posts", filter=models.Q(posts__status="published"))
            ).filter(post_count__gt=0).order_by("-post_count")[:50]
            return {"tags": [{"slug": t.slug, "name": t.name, "post_count": t.post_count} for t in tags]}
        except Exception:
            return {"tags": []}

    # ═══════════════════════════════════════════════════════════════════
    # Products
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/products")
    def list_products(request):
        """GET /api/products — Product listing."""
        try:
            from apps.pages.products.models.cart import Product
            qs = Product.objects.filter(is_active=True).order_by("title")
            total = qs.count()
            products = qs[:24]
            return {
                "data": [
                    {"id": p.pk, "title": p.title, "slug": getattr(p, "slug", ""),
                     "description": getattr(p, "description", ""),
                     "price": str(getattr(p, "price", 0)),
                     "image_url": p.image.url if getattr(p, "image", None) else None}
                    for p in products
                ],
                "pagination": {"page": 1, "per_page": 24, "total": total, "total_pages": 1},
            }
        except Exception:
            return {"data": [], "pagination": {"page": 1, "per_page": 12, "total": 0, "total_pages": 0}}

    # ═══════════════════════════════════════════════════════════════════
    # Auth (read-only — actual auth goes through allauth)
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/auth/status")
    def auth_status(request):
        """GET /api/auth/status — Current authentication status."""
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            return {
                "authenticated": True,
                "user": {"id": user.pk, "username": user.username, "email": user.email,
                         "full_name": user.get_full_name() if hasattr(user, "get_full_name") else ""},
            }
        return {"authenticated": False, "user": None}
