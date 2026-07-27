"""
Backward-compatible re-export of HTMX/SSE helpers.

The implementation now lives in ``django_fusion.plugins.htmx``.
New code should import from there.
"""

from django_fusion.plugins.htmx import (
    HtmxDetails,
    ServerSentEvent,
    SSEMixin,
    push_url,
    replace_url,
    supports_htmx,
    supports_sse,
    trigger_client_event,
)
from django_fusion.site.interface.response import HttpResponseServerSentEvents

__all__ = [
    "HtmxDetails",
    "HttpResponseServerSentEvents",
    "ServerSentEvent",
    "SSEMixin",
    "push_url",
    "replace_url",
    "supports_htmx",
    "supports_sse",
    "trigger_client_event",
]
