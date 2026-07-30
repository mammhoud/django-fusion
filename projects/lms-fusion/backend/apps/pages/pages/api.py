"""
Fusion page content API — Wagtail model-backed pages only.

All page content now comes from Wagtail fixture data.
The STATIC_PAGES fallback has been removed.
"""

import logging

from django.http import JsonResponse

from apps.pages.pages.content import normalize_slug
from django_fusion.routes import fusion_json_response, FusionCodec

logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────────


def _get_wagtail_page(slug: str):
    """Try to retrieve a live Wagtail page by slug. Returns None if not found."""
    normalized = normalize_slug(slug)
    try:
        from wagtail.models import Page

        page = Page.objects.live().filter(slug=normalized).first()
        return page
    except Exception:
        return None


def _wagtail_page_to_dict(page) -> dict:
    """Serialize a Wagtail page to a frontend-consumable dict."""
    data = {
        "id": page.pk,
        "slug": page.slug if hasattr(page, "slug") and page.slug else "home",
        "title": page.title,
        "type": page.__class__.__name__,
        "layout": getattr(page, "effective_layout", "default"),
        "fusion_render_first": bool(getattr(page, "fusion_render_first", False)),
        "fragment_name": getattr(page, "effective_fragment_name", f"pages.{page.slug}"),
        "show_in_nav": bool(getattr(page, "show_in_nav", True)),
        "seo_title": getattr(page, "seo_title", "") or page.title,
        "search_description": getattr(page, "search_description", ""),
    }

    if hasattr(page, "hero_heading"):
        data["hero_heading"] = page.hero_heading
        data["hero_subheading"] = getattr(page, "hero_subheading", "")

    if hasattr(page, "body"):
        data["body"] = page.body

    if hasattr(page, "featured_image") and page.featured_image:
        try:
            data["featured_image_url"] = page.featured_image.get_rendition("fill-1200x400").url
        except Exception:
            pass

    if hasattr(page, "custom_css") and page.custom_css:
        data["custom_css"] = page.custom_css

    try:
        children = page.get_children().live().filter(show_in_nav=True)
        data["children"] = [
            {"id": c.pk, "slug": c.slug, "title": c.title}
            for c in children
        ]
    except Exception:
        data["children"] = []

    return data


# ── Page list ───────────────────────────────────────────────────────


def page_list(request):
    """GET /api/pages/ — list all published pages (Wagtail only)."""
    try:
        from wagtail.models import Page

        pages = []
        for p in Page.objects.live().filter(depth__gt=1).order_by("title"):
            try:
                pages.append(_wagtail_page_to_dict(p))
            except Exception:
                logger.exception("page_list failed to serialize page pk=%s", p.pk)

        return JsonResponse({"pages": pages, "total": len(pages)})
    except Exception:
        return JsonResponse({"pages": [], "total": 0})


# ── Page detail ──────────────────────────────────────────────────────


def page_detail(request, slug):
    """GET /api/pages/<slug>/ — return page content (Wagtail only)."""
    normalized = normalize_slug(slug)

    wagtail_page = _get_wagtail_page(slug)
    if wagtail_page is not None:
        return JsonResponse(_wagtail_page_to_dict(wagtail_page))

    return JsonResponse({"status": "error", "message": "Page not found"}, status=404)



# ── Page fragment pointer ────────────────────────────────────────────


def page_fragment(request, slug):
    """GET /api/pages/<slug>/fragment/ — fragment pointer for fusion rendering."""
    try:
        normalized = normalize_slug(slug)

        wagtail_page = _get_wagtail_page(slug)
        if wagtail_page is None:
            return fusion_json_response({"error": "Page not found"}, status=404)

        from apps.core.api.data_adapter import fusion_response

        page_info = _wagtail_page_to_dict(wagtail_page)
        fragment_name = page_info.get("fragment_name") or f"pages.{normalized.replace('-', '_')}"
        pointer = fusion_response(
            fragment_name, request,
            extra={
                "page_slug": normalized,
                "title": page_info.get("title", normalized),
                "layout": page_info.get("layout", "default"),
                "fusion_render_first": page_info.get("fusion_render_first", False),
            },
        )
        return fusion_json_response(data=pointer, status=200)
    except Exception:
        logger.exception("page_fragment error for slug=%s", slug)
        return fusion_json_response({"error": "Internal server error"}, status=500)


# ── Page data/HTML ───────────────────────────────────────────────────


def page_data(request, slug):
    """GET /api/pages/<slug>/data/ — unified page endpoint (JSON)."""
    try:
        normalized = normalize_slug(slug)

        wagtail_page = _get_wagtail_page(slug)
        if wagtail_page is None:
            return fusion_json_response({"error": "Page not found"}, status=404)

        page_data_dict = _wagtail_page_to_dict(wagtail_page)
        encoded = FusionCodec.encode(page_data_dict)
        return fusion_json_response(
            data={"slug": normalized, "title": wagtail_page.title, "encoded": encoded},
            status=200,
        )
    except Exception:
        logger.exception("page_data error for slug=%s", slug)
        return fusion_json_response({"error": "Internal server error"}, status=500)
