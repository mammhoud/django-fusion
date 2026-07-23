"""Backward-compatibility re-exports for django_fusion.site.plugins.

The implementation moved to ``django_fusion.ci.plugins``.
"""
from django_fusion.ci.plugins import (  # noqa: F401
    HtmxDetails,
    SSEMixin,
    ServerSentEvent,
    push_url,
    replace_url,
    supports_htmx,
    supports_sse,
    trigger_client_event,
)

__all__ = [
    "HtmxDetails",
    "SSEMixin",
    "ServerSentEvent",
    "push_url",
    "replace_url",
    "supports_htmx",
    "supports_sse",
    "trigger_client_event",
]
