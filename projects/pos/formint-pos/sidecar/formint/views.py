"""
Formint — URL-facing views (thin delegation layer).

The rendering logic lives in ``formint.handlers`` (class-based HTMX fragment
handlers) and ``formint.fusion`` (dual-mode render contract) — mirroring
landing-fusion's ``apps/handlers/views.py`` + ``apps/pages/api.py`` split.
These function views exist to keep URL patterns stable while delegating to
the handler classes.

Also exposes the fusion render-mode API at the fragment path (``/fusion/``),
which the Astro shell can query before/after HTMX swaps.
"""

from django.http import HttpRequest, HttpResponse, JsonResponse

from .fusion import assets_api, navigation_api, render_mode_api
from .handlers import (
    BranchSummaryHandler,
    FormFragmentHandler,
    FusionBranchSummaryHandler,
    TableFragmentHandler,
    get_handler_response,
)

__all__ = [
    "health",
    "branch_summary",
    "fusion_branch_summary",
    "table_fragment",
    "form_fragment",
    "render_mode",
    "navigation",
    "assets",
]


def health(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok", "product": "formint-pos", "phase": 2})


def branch_summary(request: HttpRequest) -> HttpResponse:
    """Delegate to BranchSummaryHandler (render-first vs HTMX data-only)."""
    return get_handler_response(BranchSummaryHandler, request)


def fusion_branch_summary(request: HttpRequest) -> HttpResponse:
    """Delegate to FusionBranchSummaryHandler (explicit fusion renderer test)."""
    return get_handler_response(FusionBranchSummaryHandler, request)


def table_fragment(request: HttpRequest, resource: str) -> HttpResponse:
    """GET /htmx/tables/<resource>/ — delegate to TableFragmentHandler."""
    return get_handler_response(TableFragmentHandler, request, resource)


def form_fragment(request: HttpRequest, resource: str) -> HttpResponse:
    """GET/POST /htmx/forms/<resource>/ — delegate to FormFragmentHandler."""
    return get_handler_response(FormFragmentHandler, request, resource)


# ── Fusion render-mode contract (fragment-path mirror of /api/v1) ──────────

def render_mode(request: HttpRequest) -> JsonResponse:
    """GET /fusion/render-mode/ — report the active fusion render mode."""
    return render_mode_api(request)


def navigation(request: HttpRequest) -> JsonResponse:
    """GET /fusion/navigation/ — nav items from FormintSite."""
    return navigation_api(request)


def assets(request: HttpRequest) -> JsonResponse:
    """GET /fusion/assets/ — FUSION_ASSETS manifest for bundle parity."""
    return assets_api(request)
