"""
Fusion page content API — serves both static pages and Wagtail FusionPage models.

Priority: Wagtail model-backed pages first, falling back to STATIC_PAGES for
backward compatibility. When matching Wagtail page models are available, this
module returns full page context including layout, fusion_render_first, body
HTML, and featured image URLs.
"""

import logging
from pathlib import Path

from django.http import HttpResponse
from django.template import engines

from apps.pages.pages.content import STATIC_PAGES, normalize_slug
from apps.core.api.data_adapter import bolt_view, fusion_response
from django_fusion.routes import fusion_json_response, FusionCodec

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
    """Try to retrieve a Wagtail page by slug.

    Priority:
    1. Fusion-specific page models (FusionHomePage, FusionContentPage)
    2. Base wagtailcore.Page (fallback for fixture data using the base type)
    """
    normalized = normalize_slug(slug)
    try:
        from apps.pages.pages.models import FusionHomePage, FusionContentPage
        from wagtail.models import Page

        # 1. Try Fusion-specific page models
        if normalized == "home":
            fusion_page = FusionHomePage.objects.live().first()
            if fusion_page is not None:
                return fusion_page
        else:
            fusion_page = FusionContentPage.objects.live().filter(slug=normalized).first()
            if fusion_page is not None:
                return fusion_page

        # 2. Fall back to base wagtailcore.Page by slug
        return Page.objects.live().filter(slug=normalized).first()
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
    """GET /api/pages/ — list all published Fusion pages."""
    try:
        from apps.pages.pages.models import FusionHomePage, FusionContentPage
        from wagtail.models import Page

        pages = []

        # 1. Try Fusion-specific page models first
        home = FusionHomePage.objects.live().first()
        if home:
            pages.append(_wagtail_page_to_dict(home))

        for p in FusionContentPage.objects.live().filter(show_in_nav=True).order_by("title"):
            pages.append(_wagtail_page_to_dict(p))

        # 2. Fall back to base wagtailcore.Page when no Fusion pages exist
        #    (e.g., when fixtures use the base Page type rather than Fusion subtypes)
        if not pages:
            root = Page.objects.filter(depth=1).first()
            if root:
                live_children = root.get_children().live()
                for child in live_children:
                    pages.append(_wagtail_page_to_dict(child))
                # Also grab grand-children shown in menus for deeper navigation
                for child in live_children:
                    for grandchild in child.get_children().live().filter(show_in_menus=True):
                        pages.append(_wagtail_page_to_dict(grandchild))

        return {"pages": pages, "total": len(pages)}
    except Exception:
        logger.exception("page_list error")
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
            # Use getattr for fusion-specific fields — base wagtailcore.Page
            # objects (e.g., from fixtures) don't have these attributes.
            fragment_name = getattr(
                wagtail_page, "effective_fragment_name",
                f"pages.{normalized}",
            )
            pointer = fusion_response(
                fragment_name, request,
                extra={
                    "page_slug": normalized,
                    "title": wagtail_page.title,
                    "layout": getattr(wagtail_page, "effective_layout", "default"),
                    "fusion_render_first": bool(
                        getattr(wagtail_page, "fusion_render_first", False)
                    ),
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
    """Render a Wagtail FusionPage as HTML via its template.

    Falls back to a simple JSON response for base ``wagtailcore.Page``
    objects that don't have Fusion-specific view classes.
    """
    try:
        from apps.pages.pages.components import FusionContentPageView, FusionHomePageView

        is_home = page.__class__.__name__ == "FusionHomePage"
        if is_home:
            view_cls = FusionHomePageView
        elif page.__class__.__name__ == "FusionContentPage":
            view_cls = FusionContentPageView
        else:
            # Base wagtailcore.Page — no Fusion view available.
            # Return a simple JSON response instead of crashing.
            data = _wagtail_page_to_dict(page)
            encoded = FusionCodec.encode(data)
            return fusion_json_response(
                data={
                    "slug": page.slug,
                    "title": page.title,
                    "encoded": encoded,
                },
                status=200,
            )

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
