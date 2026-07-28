"""
Static public page content API for the CTC Research frontend.

The response shape intentionally mirrors Wagtail page concepts: top-level SEO
metadata plus ordered content blocks that can represent headings, rich text,
CTAs, media, FAQ groups, stats, and contact methods. When matching Wagtail page
models are introduced, this module can swap `STATIC_PAGES` for model-backed
serializers without changing the frontend contract.

Page data lives in ``plugins.pages.content`` — import from there rather than
redefining ``STATIC_PAGES`` here.
"""

import logging
from pathlib import Path

from django.http import HttpResponse
from django.template import engines

from plugins.pages.content import STATIC_PAGES, normalize_slug
from www.api.data_adapter import bolt_view, fusion_response
from django_fusion.routes import fusion_json_response, FusionCodec

logger = logging.getLogger(__name__)


# ── Helper: extract fusion_render_first from request ────────────────


def _get_fusion_render_first_from_request(request) -> bool | None:
    """Check the request for a ``fusion_render_first`` directive.

    Priority:
    1. ``X-Fusion-Render-First`` HTTP header (string "true" / "false").
    2. ``fusion_render_first`` query parameter (string "true" / "false").
    3. ``None`` — not specified; caller should use its own default.
    """
    # Header check
    header_val = request.headers.get("X-Fusion-Render-First")
    if header_val is not None:
        return header_val.strip().lower() == "true"

    # Query param check
    query_val = request.GET.get("fusion_render_first")
    if query_val is not None:
        return query_val.strip().lower() == "true"

    return None


# ── Unified page endpoint (render-first aware) ──────────────────────


def page_data(request, slug):
    """GET /api/pages/<slug>/data/ — unified page endpoint.

    Checks the request for a ``fusion_render_first`` directive (via
    ``X-Fusion-Render-First`` header or ``?fusion_render_first=true``
    query parameter) and responds accordingly:

    * ``fusion_render_first=true``  → renders the page as HTML using the
      django-fusion ``FragmentRequestRenderer`` with page data as
      template context, and returns an ``HttpResponse``.
    * ``fusion_render_first=false`` → encodes the page data with
      ``FusionCodec.encode()`` and returns it inside the standard
      ``{status, message, data}`` envelope.
    * Not specified                  → same as ``false`` (get JSON data).

    This eliminates the two-step fragment-pointer dance: a single
    request that asks for HTML or JSON based on the caller's preference.
    """
    try:
        normalized = normalize_slug(slug)
        page = STATIC_PAGES.get(normalized)
        if page is None:
            return fusion_json_response({"error": "Page not found"}, status=404)

        render_first = _get_fusion_render_first_from_request(request)

        if render_first is True:
            # ── Render HTML ──────────────────────────────────────────
            try:
                _template_path = Path(__file__).resolve().parent.parent.parent \
                    / "templates" / "pages" / "page.html"
                with open(_template_path) as f:
                    template_source = f.read()
                django_engine = engines["django"]
                template = django_engine.from_string(template_source)
                html = template.render({"page": page}, request)
                return HttpResponse(html)
            except Exception:
                logger.exception(
                    "page_data HTML render failed for slug=%s", slug
                )
                return fusion_json_response(
                    {"error": "Fragment rendering failed"},
                    status=500,
                )

        # ── Return JSON data with FusionCodec encoding ───────────────
        encoded = FusionCodec.encode(page)
        return fusion_json_response(
            data={
                "slug": normalized,
                "title": page["title"],
                "encoded": encoded,
            },
            status=200,
        )

    except Exception:
        logger.exception("page_data error for slug=%s", slug)
        return fusion_json_response({"error": "Internal server error"}, status=500)


@bolt_view
def page_detail(request, slug):
    """GET /api/pages/<slug>/ — return public page content."""
    normalized = normalize_slug(slug)
    page = STATIC_PAGES.get(normalized)
    if page is None:
        return {"status": "error", "message": "Page not found"}, 404
    return page


def page_fragment(request, slug):
    """GET /api/pages/<slug>/fragment/ — return a fragment pointer.

    Returns the enhanced ``{status, message, data: {...}}`` response envelope
    via ``fusion_json_response`` so every API consumer gets a consistent
    top-level contract.

    The frontend can use ``data.fragment_url`` to fetch the server-rendered
    HTML for this page from the django-fusion fragment renderer, falling back
    to the JSON blocks from ``page_detail`` if rendering fails.

    Note:
        The returned ``fragment_name`` follows the convention ``pages.<slug>``.
        For this demo the names are string pointers; registering matching
        ``RoutableComponent`` / ``FragmentComponent`` classes will make them
        renderable through the django-fusion fragment URL.
    """
    try:
        normalized = normalize_slug(slug)
        if normalized not in STATIC_PAGES:
            return fusion_json_response(
                {"error": "Page not found"},
                status=404,
            )

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
    except Exception:
        logger.exception("page_fragment error for slug=%s", slug)
        return fusion_json_response({"error": "Internal server error"}, status=500)
