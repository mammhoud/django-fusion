"""
Component Integration
====================
Pagination integration with Django component system.
"""

import json
import logging
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string

from django_fusion.core.context._context_mixins import PaginatedBaseMixin
logger = logging.getLogger(__name__)


class HTMXPaginationMixin(PaginatedBaseMixin):
    """
    Enhanced pagination mixin with HTMX support.
    """

    # HTMX configuration
    htmx_target: str = "#content-area"
    htmx_swap: str = "innerHTML"
    htmx_push_url: bool = True
    htmx_trigger: str | None = None

    # Load More / Infinite Scroll
    load_more_enabled: bool = False
    infinite_scroll_enabled: bool = False
    scroll_target: str = "window"
    scroll_offset: int = 100

    def get_pagination_template(self) -> str:
        """Get template for pagination controls."""
        if self.pagination_style == "load_more":
            return "components/pagination/load_more.html"
        elif self.pagination_style == "infinite":
            return "components/pagination/infinite.html"
        elif self.pagination_style == "simple":
            return "components/pagination/simple.html"
        else:
            return "components/pagination/numbers.html"

    def render_pagination_controls(self, context: dict[str, Any]) -> str:
        """Render pagination controls HTML."""
        template_name = self.get_pagination_template()
        try:
            return render_to_string(template_name, context)
        except Exception as e:
            logger.error(f"Failed to render pagination template: {e}")
            return ""

    def get_htmx_response(self, request: HttpRequest, context: dict[str, Any]) -> HttpResponse:
        """Get HTMX-optimized pagination response."""
        if not hasattr(request, "htmx") or not request.htmx:
            return None

        hx_target = request.htmx.target or self.htmx_target
        hx_swap = request.headers.get("HX-Swap", self.htmx_swap)

        if request.headers.get("HX-Trigger") == "load-more":
            return self._handle_load_more(request, context, hx_target, hx_swap)
        elif request.headers.get("HX-Trigger") == "infinite-scroll":
            return self._handle_infinite_scroll(request, context, hx_target, hx_swap)
        else:
            return self._handle_regular_pagination(request, context, hx_target, hx_swap)

    def _handle_regular_pagination(
        self,
        request: HttpRequest,
        context: dict[str, Any],
        hx_target: str,
        hx_swap: str,
    ) -> HttpResponse:
        """Handle regular pagination HTMX request."""
        items_html = self.render_items_fragment(context)
        pagination_html = self.render_pagination_controls(context)

        response = HttpResponse()

        if hx_swap == "innerHTML":
            response.write(f'<div id="items-container" hx-swap-oob="true">{items_html}</div>')
            response.write(
                f'<div id="pagination-container" hx-swap-oob="true">{pagination_html}</div>'
            )

            response["HX-Trigger"] = json.dumps(
                {
                    "pageChanged": {
                        "page": context["page_number"],
                        "total": context["total_pages"],
                    }
                }
            )
        else:
            response.write(f'<div id="items-container">{items_html}</div>')
            response.write(f'<div id="pagination-container">{pagination_html}</div>')

        if self.htmx_push_url:
            current_url = request.build_absolute_uri()
            response["HX-Push-Url"] = current_url

        return response

    def _handle_load_more(
        self,
        request: HttpRequest,
        context: dict[str, Any],
        hx_target: str,
        hx_swap: str,
    ) -> HttpResponse:
        """Handle Load More HTMX request."""
        response = HttpResponse()

        items_html = self.render_items_fragment(context)
        response.write(items_html)

        response["HX-Reswap"] = "beforeend"

        if not context["has_next"]:
            response.write('<div id="load-more-container" hx-swap-oob="delete"></div>')
        else:
            next_url = self.get_next_page_url(request, context["next_page_number"])
            response.write(
                f'<div id="load-more-container" hx-swap-oob="true">'
                f'<button hx-get="{next_url}" hx-target="#items-container" '
                f'hx-swap="beforeend" hx-trigger="click" '
                f'class="btn btn-outline-primary">Load More</button>'
                f"</div>"
            )

        response["HX-Trigger"] = json.dumps(
            {
                "itemsLoaded": {
                    "count": len(context["listed_data"]),
                    "page": context["page_number"],
                    "has_more": context["has_next"],
                }
            }
        )

        return response

    def _handle_infinite_scroll(
        self,
        request: HttpRequest,
        context: dict[str, Any],
        hx_target: str,
        hx_swap: str,
    ) -> JsonResponse:
        """Handle Infinite Scroll HTMX request (returns JSON)."""
        data = {
            "items": self.serialize_items(context["listed_data"]),
            "page": context["page_number"],
            "has_next": context["has_next"],
            "next_page_url": self.get_next_page_url(request, context["next_page_number"])
            if context["has_next"]
            else None,
            "total_pages": context["total_pages"],
            "total_count": context["total_count"],
        }

        return JsonResponse(data)

    def render_items_fragment(self, context: dict[str, Any]) -> str:
        """Render items fragment for HTMX responses."""
        return ""

    def serialize_items(self, items: list[Any]) -> list[dict[str, Any]]:
        """Serialize items for JSON responses."""
        return []

    def get_next_page_url(self, request: HttpRequest, next_page: int) -> str:
        """Generate URL for next page."""
        current_url = request.get_full_path()

        if "?" in current_url:
            base_url, query_string = current_url.split("?", 1)
            from urllib.parse import parse_qs, urlencode

            params = parse_qs(query_string)
            params[self.page_kwarg] = [str(next_page)]
            return f"{base_url}?{urlencode(params, doseq=True)}"
        else:
            return f"{current_url}?{self.page_kwarg}={next_page}"

    def get_paginated_context_with_htmx(
        self, request: HttpRequest, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Get pagination context with HTMX-specific data."""
        pagination_context = self.extend_context(request, context)

        if hasattr(request, "htmx") and request.htmx:
            pagination_context.update(
                {
                    "is_htmx_request": True,
                    "htmx_target": self.htmx_target,
                    "htmx_swap": self.htmx_swap,
                    "next_page_url": self.get_next_page_url(
                        request, pagination_context.get("next_page_number")
                    )
                    if pagination_context.get("has_next")
                    else None,
                    "load_more_enabled": self.load_more_enabled,
                    "infinite_scroll_enabled": self.infinite_scroll_enabled,
                }
            )

        return pagination_context
