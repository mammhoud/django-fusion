"""Page-specific rendering mixins for django-fusion.

This module contains integrations that belong at the page/routing boundary,
including the Wagtail ``Page`` rendering pipeline. Generic fragment context
handling remains in ``django_fusion.core.context``.
"""

from __future__ import annotations

from typing import Any

from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

from django_fusion.core.context.context import FragmentHandlerMixin
from django_fusion.plugins.htmx import is_htmx_request


class WagtailPageMixin(FragmentHandlerMixin):
    """Apply the django-fusion fragment pipeline to Wagtail pages.

    The mixin keeps Wagtail's ``get_context`` convention while sharing the
    same strategy detection and fragment rendering behavior as routed views.
    """

    def serve(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Resolve strategy, build Wagtail context, and render the response."""
        try:
            self.strategy = self.resolve_strategy(request)

            if hasattr(self, "display_mode"):
                if self.display_mode == "modal":
                    self.strategy = "fragment"
                    self._modal_requested = True
                    self._modal_size = getattr(self, "modal_size", "lg")
                else:
                    self._modal_requested = False
            else:
                self._modal_requested = False

            self.template_name = self.resolve_template_name()
            context = self.get_context(request, *args, **kwargs)

            if self.strategy == "fragment" and getattr(request, "is_unpoly", False):
                try:
                    request.up.set_title(getattr(self, "page_title", self.title))
                except Exception:
                    pass

            return self._wagtail_render(request, context)
        except Exception as exc:
            try:
                from django.shortcuts import render

                return render(
                    request,
                    "errors/nxx.html",
                    {
                        "status_code": 500,
                        "error_title": "Internal Server Error",
                        "error_message": str(exc),
                        "exception": str(exc),
                    },
                    status=500,
                )
            except Exception:
                return HttpResponseServerError(
                    "An internal error occurred while loading the page."
                )

    def _wagtail_render(
        self, request: HttpRequest, context: dict[str, Any]
    ) -> HttpResponse:
        """Render a fragment or the Wagtail page's outer layout."""
        if self.strategy == "fragment":
            response = self._render_fragment_response(request, context)
            if getattr(self, "_modal_requested", False):
                modal_size = getattr(self, "_modal_size", "lg")
                if getattr(request, "is_unpoly", False):
                    response["X-Up-Target-Layer"] = f"new-modal .modal-{modal_size}"
                else:
                    response["HX-Trigger"] = '{"openModal": true}'
            return response
        return self._render_wagtail_layout(request, context)

    def _render_fragment_response(
        self,
        request: HttpRequest,
        context: dict[str, Any],
        title: str = "",
    ) -> HttpResponse:
        """Render the page content template directly for a fragment request."""
        context.update({"is_fragment": True})
        response = TemplateResponse(request, self.template_name, context)
        if is_htmx_request(request):
            response["HX-Reswap"] = "innerHTML"
        return response

    def _render_wagtail_layout(
        self, request: HttpRequest, context: dict[str, Any]
    ) -> HttpResponse:
        """Render the outer Wagtail template for a full page request."""
        outer = getattr(self, "template", "base_page.html")
        return TemplateResponse(request, outer, context)

    def _render_layout_response(self, context: dict[str, Any]) -> HttpResponse:
        """Support the generic renderer contract when called on a page."""
        request = getattr(self, "request", None)
        if request is None:
            return HttpResponseServerError("Rendering failed: no request available.")
        return self._render_wagtail_layout(request, context)

    def get_context(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        """Add fusion strategy and template keys to Wagtail context."""
        context: dict[str, Any] = {}
        if hasattr(super(), "get_context"):
            context = super().get_context(request, *args, **kwargs)  # type: ignore[misc]

        is_fragment = self.strategy == "fragment"
        is_modal = getattr(self, "_modal_requested", False)
        context.update(
            {
                "strategy": self.strategy,
                "is_fragment_request": is_fragment,
                "is_modal": is_modal,
                "modal_size": getattr(self, "_modal_size", "lg") if is_modal else None,
                "page_title": getattr(self, "page_title", getattr(self, "title", "")),
                "layout_path": getattr(self, "layout_path", "landing/skeleton.html"),
                "template_name": self.template_name if not is_fragment else None,
                "fragment_name": self.get_fragment_name() if is_fragment else None,
            }
        )
        return context
