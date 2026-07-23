"""Core renderer for URL-driven fragment requests."""
from __future__ import annotations

import re
from typing import Any

from django.http import HttpResponse, HttpResponseBadRequest, StreamingHttpResponse
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from django_fusion.site.interface._context_mixins import is_htmx_request, is_fragment_request

from .sse import SSHTMXFragmentStreamer


# Allowed characters in a dotted fragment name: alphanumerics, underscore, dash, dot.
_FRAGMENT_NAME_RE = re.compile(r"^[\w\-]+(\.[\w\-]+)*$")


def validate_fragment_name(name: str) -> None:
    """Raise ValueError if the fragment name contains unsafe characters."""
    if not name:
        raise ValueError("Fragment name is required.")
    if not _FRAGMENT_NAME_RE.match(name):
        raise ValueError(f"Invalid fragment name: {name!r}")


def resolve_template(fragment_name: str) -> str:
    """Convert a dotted fragment name into a template path.

    Example::

        >>> resolve_template("components.home.hero")
        "components/home/hero.html"
    """
    validate_fragment_name(fragment_name)
    return f"{fragment_name.replace('.', '/')}.html"


class FragmentRequestRenderer:
    """Render a template fragment by dotted name on demand.

    Supports HTMX/Unpoly ``HttpResponse`` and SSE ``StreamingHttpResponse``.
    """

    def __init__(self, request, *, context: dict[str, Any] | None = None) -> None:
        self.request = request
        self.base_context = context or {}

    def render(self, fragment_name: str, context: dict[str, Any] | None = None) -> HttpResponse:
        """Render *fragment_name* and return an response.

        If the request advertises ``Accept: text/event-stream``, a
        ``StreamingHttpResponse`` is returned.  Otherwise a normal
        ``HttpResponse`` is returned, with HTMX headers when appropriate.
        """
        if not fragment_name:
            return HttpResponseBadRequest("Fragment name is required.")

        try:
            template_name = resolve_template(fragment_name)
        except ValueError as exc:
            return HttpResponseBadRequest(str(exc))

        merged_context = {**self.base_context, **(context or {})}

        # SSE transport
        accept = self.request.META.get("HTTP_ACCEPT", "")
        if "text/event-stream" in accept:
            streamer = SSHTMXFragmentStreamer(self.request, template_name, merged_context)
            return StreamingHttpResponse(streamer.stream(), content_type="text/event-stream")

        # Standard HTML fragment
        try:
            html = render_to_string(template_name, merged_context, request=self.request)
        except TemplateDoesNotExist:
            return HttpResponseBadRequest(f"Fragment template not found: {template_name}")

        response = HttpResponse(html)
        if is_htmx_request(self.request):
            response["HX-Reswap"] = "innerHTML"
        elif is_fragment_request(self.request):
            # Unpoly / other fragment-aware clients
            response["X-Up-Target"] = f"#{fragment_name.replace('.', '-')}"  # type: ignore[assignment]
        return response

    def render_oob(self, fragment_name: str, element_id: str, context: dict[str, Any] | None = None) -> str:
        """Render an out-of-band fragment wrapped with ``hx-swap-oob``.

        Returns the raw HTML string suitable for appending to an existing
        fragment response.
        """
        try:
            template_name = resolve_template(fragment_name)
        except ValueError:
            return ""

        merged_context = {
            **self.base_context,
            "fragment_id": element_id,
            **(context or {}),
        }
        html = render_to_string(template_name, merged_context, request=self.request)
        if "hx-swap-oob" not in html:
            html = f'<div id="{element_id}" hx-swap-oob="true">{html}</div>'
        return html
