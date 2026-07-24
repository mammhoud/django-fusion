"""Page content API — Wagtail CMS-first with STATIC_PAGES fallback.

The response shape mirrors Wagtail page concepts: SEO metadata plus
ordered content blocks.  When Wagtail Page objects exist in the database
they take priority; otherwise the legacy STATIC_PAGES dict is the fallback.

Run ``manage.py seed_pages_from_static`` to populate Wagtail from the
static dict and transition fully to CMS-managed content.
"""

import logging
from pathlib import Path

from django.http import HttpResponse
from django.template import engines
from wagtail.models import Page

from plugins.pages.content import normalize_slug, get_page_for_language
from www.api.data_adapter import bolt_view, fusion_response
from www.content.models.pages import page_to_dict
from django_fusion.routes import fusion_json_response, FusionCodec

logger = logging.getLogger(__name__)


def _get_cms_page(slug: str, language: str) -> dict | None:
    """Return page data for *slug* from Wagtail CMS or STATIC_PAGES fallback.

    Priority:
    1. Wagtail Page.objects.live() — CMS-managed content
    2. get_page_for_language() — STATIC_PAGES fallback (legacy/migration)
    """
    normalized = normalize_slug(slug)
    try:
        page = Page.objects.live().filter(slug=normalized).first()
        if page is not None:
            return page_to_dict(page.specific)
    except Exception:
        logger.info("Wagtail page query unavailable for slug=%s — using static fallback", slug)
    return get_page_for_language(slug, language)


# ── Helper: extract fusion_render_first from request ────────────────


def _get_fusion_render_first_from_request(request) -> bool | None:
    """Check the request for a ``fusion_render_first`` directive."""
    header_val = request.headers.get("X-Fusion-Render-First")
    if header_val is not None:
        return header_val.strip().lower() == "true"
    query_val = request.GET.get("fusion_render_first")
    if query_val is not None:
        return query_val.strip().lower() == "true"
    return None


# ── Unified page endpoint (render-first aware) ──────────────────────


def page_data(request, slug):
    """GET /apis/pages/<slug>/data/ — unified page endpoint."""
    try:
        normalized = normalize_slug(slug)
        language = getattr(request, "LANGUAGE_CODE", "en")
        page = _get_cms_page(slug, language)
        if page is None:
            return fusion_json_response({"error": "Page not found"}, status=404)

        render_first = _get_fusion_render_first_from_request(request)

        if render_first is True:
            try:
                _template_path = (
                    Path(__file__).resolve().parent.parent.parent
                    / "templates" / "pages" / "page.html"
                )
                with open(_template_path) as f:
                    template_source = f.read()
                django_engine = engines["django"]
                template = django_engine.from_string(template_source)
                html = template.render({"page": page}, request)
                return HttpResponse(html)
            except Exception:
                logger.exception("page_data HTML render failed for slug=%s", slug)
                return fusion_json_response(
                    {"error": "Fragment rendering failed"}, status=500
                )

        encoded = FusionCodec.encode(page)
        return fusion_json_response(
            data={
                "slug": normalized,
                "title": page["title"],
                "encoded": encoded,
                "language": language,
            },
            status=200,
        )
    except Exception:
        logger.exception("page_data error for slug=%s", slug)
        return fusion_json_response({"error": "Internal server error"}, status=500)


@bolt_view
def page_detail(request, slug):
    """GET /apis/pages/<slug>/ — return public page content."""
    language = getattr(request, "LANGUAGE_CODE", "en")
    page = _get_cms_page(slug, language)
    if page is None:
        return {"status": "error", "message": "Page not found"}, 404
    return page


def page_fragment(request, slug):
    """GET /apis/pages/<slug>/fragment/ — return a fragment pointer."""
    try:
        normalized = normalize_slug(slug)
        language = getattr(request, "LANGUAGE_CODE", "en")
        page = _get_cms_page(slug, language)
        if page is None:
            return fusion_json_response({"error": "Page not found"}, status=404)

        fragment_name = f"pages.{normalized.replace('-', '_')}"
        pointer = fusion_response(
            fragment_name,
            request,
            extra={
                "page_slug": normalized,
                "title": page["title"],
                "language": language,
            },
        )
        return fusion_json_response(data=pointer, status=200)
    except Exception:
        logger.exception("page_fragment error for slug=%s", slug)
        return fusion_json_response({"error": "Internal server error"}, status=500)
