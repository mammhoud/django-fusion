import json
import logging
from collections.abc import Generator, Iterable
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import (
    HttpResponse,
    HttpResponseRedirectBase,
    StreamingHttpResponse,
)

logger = logging.getLogger(__name__)

from django_fusion.plugins.htmx.core import HtmxDetails, ServerSentEvent

# ============================================================================
# HTMX RESPONSE CLASSES
# ============================================================================
EventStream = Iterable["ServerSentEvent"] | Generator["ServerSentEvent", None, None]


class HttpResponseStopPolling(HttpResponse):
    """HTMX-only: Stop polling (status 286)."""

    status_code = 286
    reason_phrase = "Stop Polling"


class HttpResponseClientRedirect(HttpResponseRedirectBase):
    """HTMX client-side redirect via HX-Redirect."""

    status_code = 200

    def __init__(self, redirect_to: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(redirect_to, *args, **kwargs)
        self["HX-Redirect"] = self["Location"]
        del self["Location"]


class HttpResponseClientRefresh(HttpResponse):
    """HTMX full page refresh."""

    def __init__(self) -> None:
        super().__init__()
        self["HX-Refresh"] = "true"


class HttpResponseLocation(HttpResponseRedirectBase):
    """Advanced HTMX redirect with swap/target control."""

    status_code = 200

    def __init__(
        self,
        redirect_to: str,
        *args: Any,
        source: str | None = None,
        event: str | None = None,
        target: str | None = None,
        swap: str | None = None,
        select: str | None = None,
        values: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(redirect_to, *args, **kwargs)
        spec: dict[str, Any] = {"path": self["Location"]}
        del self["Location"]

        for key, value in {
            "source": source,
            "event": event,
            "target": target,
            "swap": swap,
            "select": select,
            "headers": headers,
            "values": values,
        }.items():
            if value:
                spec[key] = value

        self["HX-Location"] = json.dumps(spec, cls=DjangoJSONEncoder)


class HttpResponseServerSentEvents(StreamingHttpResponse):
    """Streaming response for SSE events."""

    def __init__(self, stream: EventStream, *args: Any, **kwargs: Any) -> None:
        def event_generator():
            for event in stream:
                yield event.encode() if isinstance(event, ServerSentEvent) else event

        super().__init__(
            content=event_generator(), content_type="text/event-stream", *args, **kwargs
        )
        self["Cache-Control"] = "no-cache"
        self["X-Accel-Buffering"] = "no"


class HtmxResponseMixin:
    """HTMX-aware view mixin with CSP and partial rendering."""

    def dispatch(self, request, *args, **kwargs):
        request.htmx = getattr(request, "htmx", HtmxDetails(request))

        response = super().dispatch(request, *args, **kwargs)

        if not response.headers.get("Content-Security-Policy"):
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self'"
            )

        return response
