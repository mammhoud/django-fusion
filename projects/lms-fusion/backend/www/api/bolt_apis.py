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
        from plugins.pages.content import STATIC_PAGES, normalize_slug

        normalized = normalize_slug(slug)
        page = STATIC_PAGES.get(normalized)
        if page is None:
            return {"status": "error", "message": "Page not found"}, 404
        return page

    @bolt.get("/pages/<slug>/fragment")
    def page_fragment_pointer(request, slug):
        """GET /api/pages/<slug>/fragment — Fragment pointer with fusion metadata."""
        from plugins.pages.content import STATIC_PAGES, normalize_slug
        from www.api.data_adapter import fusion_response
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
    # Branding API
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/fusion/branding")
    def branding(request):
        """GET /api/fusion/branding — Dynamic site branding."""
        try:
            from plugins.branding.context_processors import fusion_branding_context

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
    # Courses (LMS-specific)
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/courses")
    def list_courses(request):
        """GET /api/courses — Course catalog."""
        try:
            from plugins.lms.models.course import Course

            qs = Course.objects.filter(is_published=True).order_by("-created_at")
            page = _qp_int(request, "page", 1)
            per_page = _qp_int(request, "per_page", 12)
            total = qs.count()
            items = qs[(page - 1) * per_page : page * per_page]

            return {
                "data": [
                    {
                        "id": c.pk,
                        "title": c.title,
                        "slug": getattr(c, "slug", ""),
                        "description": getattr(c, "description", ""),
                        "price": float(getattr(c, "price", 0)),
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                    }
                    for c in items
                ],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": max(1, (total + per_page - 1) // per_page),
                },
            }
        except Exception:
            return {"data": [], "pagination": {"page": 1, "per_page": 12, "total": 0, "total_pages": 0}}

    # ═══════════════════════════════════════════════════════════════════
    # Blog posts
    # ═══════════════════════════════════════════════════════════════════

    @bolt.get("/blog")
    def list_blog_posts(request):
        """GET /api/blog — Blog post listing."""
        try:
            from plugins.blog.models.post import Post

            qs = Post.objects.filter(is_published=True).order_by("-published_at")
            page = _qp_int(request, "page", 1)
            per_page = _qp_int(request, "per_page", 12)
            total = qs.count()
            items = qs[(page - 1) * per_page : page * per_page]

            return {
                "data": [
                    {
                        "id": p.pk,
                        "title": p.title,
                        "slug": getattr(p, "slug", ""),
                        "excerpt": getattr(p, "excerpt", ""),
                        "published_at": p.published_at.isoformat() if p.published_at else None,
                    }
                    for p in items
                ],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": max(1, (total + per_page - 1) // per_page),
                },
            }
        except Exception:
            return {"data": [], "pagination": {"page": 1, "per_page": 12, "total": 0, "total_pages": 0}}
