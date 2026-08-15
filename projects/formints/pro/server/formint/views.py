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

from pathlib import Path

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .fusion import (
    assets_api,
    navigation_api,
    render_mode_api,
    session_mode_clear_api,
    session_mode_get_api,
    session_mode_set_api,
)
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
    "session_mode",
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
    """GET /fusion/navigation/ — nav items from FormintModule."""
    return navigation_api(request)


def assets(request: HttpRequest) -> JsonResponse:
    """GET /fusion/assets/ — FUSION_ASSETS manifest for bundle parity."""
    return assets_api(request)


# ── API Documentation pages ────────────────────────────────────────────

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def api_docs(request: HttpRequest) -> HttpResponse:
    """GET /api/v1/docs/ — API documentation landing page."""
    html = (_TEMPLATE_DIR / "api-docs.html").read_text()
    return HttpResponse(html, content_type="text/html; charset=utf-8")


def api_docs_swagger(request: HttpRequest) -> HttpResponse:
    """GET /api/v1/docs/swagger — Swagger UI."""
    html = (_TEMPLATE_DIR / "swagger.html").read_text()
    return HttpResponse(html, content_type="text/html; charset=utf-8")


def api_docs_redoc(request: HttpRequest) -> HttpResponse:
    """GET /api/v1/docs/redoc — ReDoc."""
    html = (_TEMPLATE_DIR / "redoc.html").read_text()
    return HttpResponse(html, content_type="text/html; charset=utf-8")


@csrf_exempt
def session_mode(request: HttpRequest) -> JsonResponse:
    """Settings-UI toggle for the per-session render-mode preference.

    GET    → report current state (effective mode, session cache, default)
    POST   → store an explicit preference (``{"fusion_render_first": true|false}``)
    DELETE → clear the stored preference (falls back to the default)

    All writes go through ``FusionSessionChecker`` (``set_preference`` /
    ``clear_preference``) so the stored value drives
    ``get_effective_render_first`` without the UA-seeding heuristic.

    ``@csrf_exempt`` must live on THIS URL-resolved view — Django's CSRF
    middleware only checks the view Django resolves from the URL pattern,
    not the inner helpers it delegates to. The endpoint is a benign
    per-session preference toggle served to the same-origin Astro shell.
    """
    if request.method == "POST":
        return session_mode_set_api(request)
    if request.method == "DELETE":
        return session_mode_clear_api(request)
    return session_mode_get_api(request)
