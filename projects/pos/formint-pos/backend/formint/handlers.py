"""
Formint — HTMX fragment handlers (class-based, mirroring landing-fusion).

Landing-fusion organizes its render pipeline as ``PageHandler`` subclasses in
``apps/handlers/views.py`` — one class per view, each pinning its
``template_name`` / ``fragment_name`` and implementing a small context method.
Formint mirrors that shape for its HTMX fragments:

    BranchSummaryHandler  → GET /htmx/branches/summary/
    TableFragmentHandler  → GET /htmx/tables/<resource>/
    FormFragmentHandler   → GET|POST /htmx/forms/<resource>/

Each handler owns its django-fusion component (``TableMixin`` / ``FormMixin`` /
``FragmentComponent``) and returns the same lean HTMX fragment contract the
Astro shell swaps in — with the dual-mode render-first option honoured via
``X-Fusion-Render-First`` (see ``formint/fusion.py``).
"""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from django_fusion.fragments import FragmentRequestRenderer
from django_fusion.routes.rendering.renderers import fusion_json_response

from formint.components import FORM_COMPONENTS, TABLE_COMPONENTS
from formint.fusion import get_effective_render_first
from formint.fusion_components import BranchSummaryFragment

__all__ = [
    "BranchSummaryHandler",
    "TableFragmentHandler",
    "FormFragmentHandler",
    "get_handler_response",
]


def _not_htmx(payload: dict[str, Any]) -> JsonResponse:
    return JsonResponse(payload, status=406)


class BranchSummaryHandler:
    """Branch section fragment — django-fusion render-first or HTMX data-only.

    ``X-Fusion-Render-First: true`` is the explicit migration-proof path; the
    normal Astro section uses the lean response and owns its shell/skeleton.
    Both paths share the same component context and therefore the same domain
    contract; only presentation transport differs.
    """

    component_class = BranchSummaryFragment
    template_name = "formint/branch_summary.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.headers.get("HX-Request") != "true":
            return _not_htmx(
                {
                    "detail": "This endpoint is an HTMX data fragment.",
                    "product": "formint-pos",
                }
            )

        component = self.component_class()
        component.setup(request)
        # NOTE: we consult get_effective_render_first() directly (mirroring
        # landing-fusion's helper) rather than the mixin's dispatch, so the
        # component-level force_data_mode / force_render_first / session
        # preference are not consulted here — header + settings default only.
        if get_effective_render_first(request):
            response = component.render_fragment_response(component.get_fragment_context())
            response["X-Formint-Response-Mode"] = "django-fusion-fragment"
        else:
            context = component.get_fragment_context()
            response = render(request, self.template_name, context)
            response["X-Formint-Response-Mode"] = "htmx-data-only"

        response["Cache-Control"] = "no-store"
        return response


class FusionBranchSummaryHandler(BranchSummaryHandler):
    """Expose the shared django-fusion renderer for an explicit first-load test."""

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.headers.get("HX-Request") != "true":
            return _not_htmx({"detail": "HTMX required"})

        renderer = FragmentRequestRenderer(
            request,
            context={
                "branches": 0,
                "orders_today": 0,
                "sync_status": "Planned",
            },
        )
        response = renderer.render("formint.branch_summary")
        response["X-Formint-Response-Mode"] = "django-fusion-fragment"
        return response


class TableFragmentHandler:
    """GET /htmx/tables/<resource>/ — server-rendered data table fragment.

    Uses the django-fusion ``TableMixin`` + ``RowGenerator`` data component.
    Returns the table region only; Astro owns the surrounding shell.
    """

    def get(self, request: HttpRequest, resource: str) -> HttpResponse:
        component_cls = TABLE_COMPONENTS.get(resource)
        if component_cls is None:
            return JsonResponse(
                {
                    "detail": f"Unknown table resource: {resource}",
                    "available": sorted(TABLE_COMPONENTS),
                },
                status=404,
            )

        component = component_cls()
        if (
            request.headers.get("HX-Request") == "true"
            and get_effective_render_first(request)
        ):
            # django-fusion render-first path — fusion JSON envelope.
            context = component.get_table_context_data()
            return fusion_json_response(data=context, status=200)

        context = component.get_table_context_data()
        context["resource"] = resource
        context["product"] = "formint-pos"
        # Resource names use hyphens; template files use underscores.
        template = f"formint/tables/{resource.replace('-', '_')}.html"
        response = render(request, template, context)
        response["X-Formint-Response-Mode"] = "htmx-data-only"
        response["X-Formint-Table-Resource"] = resource
        response["Cache-Control"] = "no-store"
        return response


class FormFragmentHandler:
    """GET/POST /htmx/forms/<resource>/ — data-component form fragment.

    GET renders the django-fusion ``FormMixin`` model form; POST saves the
    record and returns the matching table fragment (CRUD loop for HTMX).
    """

    def get(self, request: HttpRequest, resource: str) -> HttpResponse:
        component_cls = FORM_COMPONENTS.get(resource)
        if component_cls is None:
            return JsonResponse(
                {
                    "detail": f"Unknown form resource: {resource}",
                    "available": sorted(FORM_COMPONENTS),
                },
                status=404,
            )

        component = component_cls()
        if request.method == "POST":
            # FormMixin builds form kwargs from form_kwargs (django-fusion API).
            component.form_kwargs = {
                "data": request.POST or None,
                "files": request.FILES or None,
            }
            form = component.get_form()
            if form.is_valid():
                form.save()
                return HttpResponse(
                    status=200,
                    headers={
                        "HX-Trigger": "formint-table-refresh",
                        "X-Formint-Saved": "true",
                    },
                )
            # Invalid → re-render form with errors
            context = {"form": form, "resource": resource, "product": "formint-pos"}
            template = f"formint/forms/{resource.replace('-', '_')}.html"
            response = render(request, template, context)
            response["X-Formint-Response-Mode"] = "htmx-form-errors"
            response["Cache-Control"] = "no-store"
            return response

        form = component.get_form()
        context = {"form": form, "resource": resource, "product": "formint-pos"}
        template = f"formint/forms/{resource.replace('-', '_')}.html"
        response = render(request, template, context)
        response["X-Formint-Response-Mode"] = "htmx-data-only"
        response["Cache-Control"] = "no-store"
        return response


# ── Dispatch helper (kept for function-view compatibility) ─────────────────

def get_handler_response(handler_cls, request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Instantiate a handler and dispatch GET/POST to it (thin compatibility layer).

    Handlers that treat POST internally (e.g. ``FormFragmentHandler.get``
    implements the full GET+POST form loop) declare only ``get``; any request
    method falls back to it when no method-specific handler exists.
    """
    handler = handler_cls()
    method = getattr(handler, request.method.lower(), None)
    if method is None:
        method = getattr(handler, "get", None)
    if method is None:
        return HttpResponse(status=405)
    return method(request, *args, **kwargs)
