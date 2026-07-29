"""CMS Fusion page content API — Wagtail model-backed with STATIC_PAGES fallback.

Priority: Wagtail model-backed pages first, falling back to STATIC_PAGES for
backward compatibility. When matching Wagtail page models are available, this
module returns full page context including layout, fusion_render_first, body
HTML, and featured image URLs.

Endpoints:
    GET  /api/pages/               → page_list (all published pages)
    GET  /api/pages/<slug>/        → page_detail (single page, Wagtail first)
    GET  /api/pages/<slug>/fragment/ → page_fragment (fragment pointer)
    GET  /api/pages/<slug>/data/     → page_data (JSON or HTML based on render_first)
"""

import logging
from pathlib import Path

from django.http import HttpResponse
from django.template import engines

from apps.core.api.data_adapter import bolt_view, fusion_response
from apps.pages.pages.content import STATIC_PAGES, normalize_slug
from django_fusion.routes import FusionCodec, fusion_json_response

logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────────


def _get_fusion_render_first_from_request(request) -> bool | None:
    """Check request for fusion_render_first directive (header or query param)."""
    header_val = request.headers.get("X-Fusion-Render-First")
    if header_val is not None:
        return header_val.strip().lower() == "true"
    query_val = request.GET.get("fusion_render_first")
    if query_val is not None:
        return query_val.strip().lower() == "true"
    return None


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
    """Serialize a Wagtail FusionPage to a frontend-consumable dict."""
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

    # Home page hero fields
    if hasattr(page, "hero_heading"):
        data["hero_heading"] = page.hero_heading
        data["hero_subheading"] = getattr(page, "hero_subheading", "")

    # Content page body
    if hasattr(page, "body"):
        data["body"] = page.body

    # Featured image
    if hasattr(page, "featured_image") and page.featured_image:
        try:
            data["featured_image_url"] = page.featured_image.get_rendition("fill-1200x400").url
        except Exception:
            pass

    # Custom CSS
    if hasattr(page, "custom_css") and page.custom_css:
        data["custom_css"] = page.custom_css

    # Child pages for navigation
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


@bolt_view
def page_list(request):
    """GET /api/pages/ — list all published pages (Wagtail + static fallback)."""
    try:
        from wagtail.models import Page

        pages = []
        for p in Page.objects.live().filter(depth__gt=1).order_by("title"):
            try:
                pages.append(_wagtail_page_to_dict(p))
            except Exception:
                logger.exception("page_list failed to serialize page pk=%s", p.pk)

        # Fallback to static pages if the Wagtail tree has no usable pages
        if not pages:
            for static_page in STATIC_PAGES.values():
                pages.append(static_page)

        return {"pages": pages, "total": len(pages)}
    except Exception:
        return {"pages": [], "total": 0}


# ── Page detail ──────────────────────────────────────────────────────


@bolt_view
def page_detail(request, slug):
    """GET /api/pages/<slug>/ — return page content (Wagtail first, static fallback)."""
    normalized = normalize_slug(slug)

    # 1. Try Wagtail model-backed page
    wagtail_page = _get_wagtail_page(slug)
    if wagtail_page is not None:
        return _wagtail_page_to_dict(wagtail_page)

    # 2. Fall back to STATIC_PAGES
    page = STATIC_PAGES.get(normalized)
    if page is None:
        return {"status": "error", "message": "Page not found"}, 404
    return page


# ── Page fragment pointer ────────────────────────────────────────────


def page_fragment(request, slug):
    """GET /api/pages/<slug>/fragment/ — fragment pointer for fusion rendering."""
    try:
        normalized = normalize_slug(slug)

        # 1. Try Wagtail page
        wagtail_page = _get_wagtail_page(slug)
        if wagtail_page is not None:
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

        # 2. Fall back to STATIC_PAGES
        if normalized not in STATIC_PAGES:
            return fusion_json_response({"error": "Page not found"}, status=404)

        fragment_name = f"pages.{normalized.replace('-', '_')}"
        pointer = fusion_response(
            fragment_name, request,
            extra={
                "page_slug": normalized,
                "title": STATIC_PAGES[normalized]["title"],
            },
        )
        return fusion_json_response(data=pointer, status=200)
    except Exception:
        logger.exception("page_fragment error for slug=%s", slug)
        return fusion_json_response({"error": "Internal server error"}, status=500)


# ── Page data/HTML ───────────────────────────────────────────────────


def page_data(request, slug):
    """GET /api/pages/<slug>/data/ — unified page endpoint (JSON or HTML)."""
    try:
        normalized = normalize_slug(slug)
        render_first = _get_fusion_render_first_from_request(request)

        # 1. Try Wagtail page
        wagtail_page = _get_wagtail_page(slug)
        if wagtail_page is not None:
            if render_first is True:
                return _render_wagtail_html(wagtail_page, request)

            # Return JSON with FusionCodec encoding
            page_data_dict = _wagtail_page_to_dict(wagtail_page)
            encoded = FusionCodec.encode(page_data_dict)
            return fusion_json_response(
                data={"slug": normalized, "title": wagtail_page.title, "encoded": encoded},
                status=200,
            )

        # 2. Fall back to STATIC_PAGES
        page = STATIC_PAGES.get(normalized)
        if page is None:
            return fusion_json_response({"error": "Page not found"}, status=404)

        if render_first is True:
            return _render_static_html(page, request, slug)

        encoded = FusionCodec.encode(page)
        return fusion_json_response(
            data={"slug": normalized, "title": page["title"], "encoded": encoded},
            status=200,
        )
    except Exception:
        logger.exception("page_data error for slug=%s", slug)
        return fusion_json_response({"error": "Internal server error"}, status=500)


def _render_wagtail_html(page, request) -> HttpResponse:
    """Render a Wagtail FusionPage as HTML via its template view."""
    try:
        from apps.pages.pages.components import FusionContentPageView, FusionHomePageView

        is_home = page.__class__.__name__ == "FusionHomePage"
        view_cls = FusionHomePageView if is_home else FusionContentPageView
        view_instance = view_cls()
        view_instance.request = request
        view_instance.args = ()
        view_instance.kwargs = {"slug": page.slug if hasattr(page, "slug") else "home"}
        # Set model_class to the page's actual model so _get_page() can look it up
        view_instance.model_class = page.__class__
        context = view_instance.get_context_data()
        return view_instance.render_to_response(context)
    except Exception:
        logger.exception("Wagtail HTML render failed for page=%s", page.pk)
        return fusion_json_response({"error": "Fragment rendering failed"}, status=500)


def _render_static_html(page_dict, request, slug) -> HttpResponse:
    """Render a STATIC_PAGES entry as HTML."""
    try:
        _template_path = (
            Path(__file__).resolve().parent.parent.parent / "templates" / "pages" / "page.html"
        )
        with open(_template_path) as f:
            template_source = f.read()
        django_engine = engines["django"]
        template = django_engine.from_string(template_source)
        html = template.render({"page": page_dict}, request)
        return HttpResponse(html)
    except Exception:
        logger.exception("Static page HTML render failed for slug=%s", slug)
        return fusion_json_response({"error": "Fragment rendering failed"}, status=500)
