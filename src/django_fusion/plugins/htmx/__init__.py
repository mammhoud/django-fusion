"""
HTMX plugin for django-fusion fragments
=======================================

Provides HTMX request detection, the ``HtmxDetails`` wrapper, SSE helpers,
and HTMX-specific response utilities.

Usage::

    from django_fusion.plugins.htmx import HtmxDetails, supports_htmx

    def my_view(request):
        if supports_htmx(request):
            target = request.htmx.target
            ...
"""

from .core import (
    HtmxDetails,
    ServerSentEvent,
    SSEMixin,
    is_htmx_request,
    push_url,
    replace_url,
    supports_htmx,
    supports_sse,
    trigger_client_event,
)

__all__ = [
    "HtmxDetails",
    "ServerSentEvent",
    "SSEMixin",
    "is_htmx_request",
    "push_url",
    "replace_url",
    "supports_htmx",
    "supports_sse",
    "trigger_client_event",
]
