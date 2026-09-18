"""Channels WebSocket routing for Loop-CRM realtime events.

Mount in ``asgi.py`` through ``URLRouter``; the consumer reuses the same
workspace group as the SSE road so both transports share one event stream.
"""
from django.urls import path

from .realtime import WorkspaceEventConsumer

websocket_urlpatterns = [
    path("ws/workspace/<int:workspace_id>/", WorkspaceEventConsumer.as_asgi(), name="workspace_events"),
]
