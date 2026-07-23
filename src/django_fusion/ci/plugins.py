import json
import logging
from typing import Any, Literal, TypeVar
from urllib.parse import unquote

from django.core.serializers.json import DjangoJSONEncoder
from django.http.request import HttpRequest
from django.http.response import (
    HttpResponseBase,
)
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

from ._context_mixins import *
from .response import *

_HTMX_RESPONSE = TypeVar("_HTMX_RESPONSE", bound=HttpResponseBase)

# ============================================================================
# CORE UTILITIES
# ============================================================================


def supports_sse(request: HttpRequest) -> bool:
    """Check if client supports Server-Sent Events."""
    return request.headers.get("Accept") == "text/event-stream"


def supports_htmx(request: HttpRequest) -> bool:
    """Check if request came from HTMX."""
    return request.headers.get("HX-Request") == "true"


# ============================================================================
# HTMX REQUEST WRAPPER
# ============================================================================


class HtmxDetails:
    """HTMX request details with URI decoding support."""

    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def __bool__(self) -> bool:
        return self.request.headers.get("HX-Request") == "true"

    @property
    def boosted(self) -> bool:
        return self._get_header("HX-Boosted") == "true"

    @property
    def current_url(self) -> str | None:
        return self._get_header("HX-Current-URL")

    @property
    def target(self) -> str | None:
        return self._get_header("HX-Target")

    @property
    def trigger(self) -> str | None:
        return self._get_header("HX-Trigger")

    @property
    def triggering_event(self) -> Any:
        value = self._get_header("Triggering-Event")
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return None

    def _get_header(self, name: str) -> str | None:
        """Get and decode header with URI decoding."""
        value = self.request.headers.get(name)
        if not value:
            return None
        if self.request.headers.get(f"{name}-URI-AutoEncoded") == "true":
            try:
                return unquote(value)
            except Exception:
                pass
        return value


# ============================================================================
# SSE CORE CLASSES
# ============================================================================


class ServerSentEvent:
    """Single SSE-compatible event with HTMX extensions."""

    def __init__(
        self,
        data: Any = None,
        html: str | None = None,
        event: str | None = None,
        id: str | None = None,
        retry: int | None = None,
        comment: str | None = None,
        head: str | None = None,
        preload: list[str] | None = None,
        target: str | None = None,
        encoder: type[json.JSONEncoder] = DjangoJSONEncoder,
    ):
        self.data = data
        self.html = html
        self.event = event
        self.id = id
        self.retry = retry
        self.comment = comment
        self.head = head
        self.preload = preload
        self.target = target
        self.encoder = encoder

    def encode(self) -> bytes:
        """Serialize to SSE wire format."""
        lines = []

        if self.comment:
            lines.append(f": {self.comment}")
        if self.id:
            lines.append(f"id: {self.id}")
        if self.event:
            lines.append(f"event: {self.event}")
        if self.retry:
            lines.append(f"retry: {self.retry}")
        if self.head:
            lines.append(f"head: {json.dumps(self.head)}")
        if self.preload:
            lines.append(f"preload: {json.dumps(self.preload)}")
        if self.target:
            lines.append(f"target: {self.target}")

        if self.html:
            lines.append(f"html: {json.dumps(self.html)}")
            for line in self.html.splitlines():
                lines.append(f"data: {line}")
        elif self.data:
            if not isinstance(self.data, str):
                try:
                    self.data = json.dumps(self.data, cls=self.encoder)
                except Exception:
                    self.data = str(self.data)
            for line in self.data.splitlines():
                lines.append(f"data: {line}")

        return "\n".join(lines).encode("utf-8") + b"\n\n"


# ============================================================================
# SSE MIXIN
# ============================================================================


class SSEMixin:
    """Reusable SSE response mixin."""

    @staticmethod
    def build_sse_event(event: str, data: dict) -> ServerSentEvent:
        """Create SSE event with data."""
        return ServerSentEvent(event=event, data=data, retry=3000)

    def sse_response(self, event: str, data: dict) -> HttpResponseServerSentEvents:
        """Create StreamingHttpResponse with single SSE event."""

        def stream():
            yield self.build_sse_event(event, data)

        return HttpResponseServerSentEvents(stream())

    def send_notify(self, message: str, level: str = "error", **extra):
        """Send notification event."""
        data = {"message": message, "level": level, **extra}
        return self.sse_response("notify", data)

    def send_redirect(self, url: str, **extra):
        """Send redirect event."""
        data = {"url": url, **extra}
        return self.sse_response("redirect", data)

    def send_fragment(
        self,
        target: str,
        template: str | None = None,
        html: str | None = None,
        context: dict | None = None,
        **extra,
    ):
        """Send HTML fragment update."""
        if html is None and template:
            html = render_to_string(template, context or {})
        elif html is None:
            raise ValueError("Either template or html must be provided")

        data = {"target": target, "html": html, **extra}
        return self.sse_response("fragment", data)


# ============================================================================
# VIEW MIXINS
# ============================================================================


class HtmxSSEMiddleware:
    """Middleware to add HTMX/SSE support to all requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.htmx = HtmxDetails(request)
        request.supports_sse = supports_sse(request)
        request.supports_htmx = supports_htmx(request)

        response = self.get_response(request)
        return response


# ============================================================================
# HEADER UTILITIES
# ============================================================================


def push_url(response: _HTMX_RESPONSE, url: str | Literal[False]) -> _HTMX_RESPONSE:
    """Push URL to browser history."""
    response["HX-Push-Url"] = "false" if url is False else url
    return response


def replace_url(response: _HTMX_RESPONSE, url: str | Literal[False]) -> _HTMX_RESPONSE:
    """Replace current URL in browser."""
    response["HX-Replace-Url"] = "false" if url is False else url
    return response


def trigger_client_event(
    response: _HTMX_RESPONSE,
    name: str,
    params: dict[str, Any] | None = None,
    *,
    after: Literal["receive", "settle", "swap"] = "receive",
    encoder: type[json.JSONEncoder] = DjangoJSONEncoder,
) -> _HTMX_RESPONSE:
    """Trigger HTMX client event."""
    params = params or {}
    header_map = {
        "receive": "HX-Trigger",
        "settle": "HX-Trigger-After-Settle",
        "swap": "HX-Trigger-After-Swap",
    }
    header = header_map[after]
    current = response.headers.get(header, "{}")

    try:
        data = json.loads(current)
    except json.JSONDecodeError:
        data = {}

    data[name] = params
    response.headers[header] = json.dumps(data, cls=encoder)
    return response
