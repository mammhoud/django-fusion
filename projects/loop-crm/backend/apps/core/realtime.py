"""Realtime workspace events for Loop-CRM (SSE + Channels WebSocket).

One channel-layer group per workspace carries the same typed event stream to
both transports, so a single ``publish_workspace_event`` call updates the
SSE stream (HTMX ``sse`` extension) and any open WebSocket consumer.

Event contract
--------------
Publishers send ``{"type": "workspace.event", "event": "<name>",
"data": {...}}`` to the group ``workspace_<id>``. Consumers relay it as:

* SSE      → ``event: <name>`` + ``data: {"json": ...}`` (``text/event-stream``)
* WebSocket → ``{"event": "<name>", "data": {...}}``

The group name is deterministic and workspace-scoped, so a member of one
workspace can never receive another workspace's events.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.http import HttpRequest, StreamingHttpResponse

# ---------------------------------------------------------------------------
# Group + publish helpers
# ---------------------------------------------------------------------------

EVENT_TYPE = "workspace.event"
#: Seconds a channel waits for a message before emitting an SSE keep-alive.
_KEEPALIVE_SECONDS = 20


def workspace_group(workspace_id: int | str) -> str:
    """Return the channel-layer group name for a workspace."""
    return f"workspace_{workspace_id}"


def publish_workspace_event(
    workspace_id: int | str, event: str, data: dict[str, Any] | None = None
) -> None:
    """Publish a typed event to a workspace group (sync-safe)."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        workspace_group(workspace_id),
        {"type": EVENT_TYPE, "event": event, "data": data or {}},
    )


async def apublish_workspace_event(
    workspace_id: int | str, event: str, data: dict[str, Any] | None = None
) -> None:
    """Async publish to a workspace group."""
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        workspace_group(workspace_id),
        {"type": EVENT_TYPE, "event": event, "data": data or {}},
    )


def safe_publish_workspace_event(
    workspace_id: int | str | None,
    event: str,
    data: dict[str, Any] | None = None,
) -> None:
    """Publish without letting a channel-layer outage break the write path.

    Realtime is best-effort: a mutation must never 500 because Redis is down.
    """
    if workspace_id is None:
        return
    try:
        publish_workspace_event(workspace_id, event, data)
    except Exception:  # noqa: BLE001 - realtime is non-critical
        return


async def safe_apublish_workspace_event(
    workspace_id: int | str | None,
    event: str,
    data: dict[str, Any] | None = None,
) -> None:
    """Async best-effort publish for async mutation roads (e.g. the Bolt API).

    Mirrors ``safe_publish_workspace_event``: a channel-layer outage must never
    fail the write.
    """
    if workspace_id is None:
        return
    try:
        await apublish_workspace_event(workspace_id, event, data)
    except Exception:  # noqa: BLE001 - realtime is non-critical
        return


# ---------------------------------------------------------------------------
# SSE (Server-Sent Events) — the HTMX ``sse`` road
# ---------------------------------------------------------------------------


async def _event_stream(workspace_id: int | str):
    """Yield ``text/event-stream`` frames for one workspace group.

    The generator subscribes to the group, then forwards ``workspace.event``
    messages. A ``finally`` block unsubscribes when the client disconnects
    (daphne cancels the streaming task, which runs the cleanup).
    """
    channel_layer = get_channel_layer()
    group = workspace_group(workspace_id)
    channel_name = await channel_layer.new_channel(prefix="loop-sse")
    await channel_layer.group_add(group, channel_name)
    try:
        # Standard SSE retry hint so clients reconnect on a dropped stream.
        yield "retry: 3000\n\n"
        while True:
            try:
                message = await asyncio.wait_for(
                    channel_layer.receive(channel_name), timeout=_KEEPALIVE_SECONDS
                )
            except asyncio.TimeoutError:
                # Comment line keeps proxies/load balancers from closing an
                # otherwise-idle connection.
                yield ": keep-alive\n\n"
                continue
            if message.get("type") != EVENT_TYPE:
                continue
            event = str(message.get("event", "message"))
            data = json.dumps(message.get("data") or {})
            yield f"event: {event}\ndata: {data}\n\n"
    finally:
        await channel_layer.group_discard(group, channel_name)


async def workspace_events_sse(
    request: HttpRequest, workspace_id: int
) -> StreamingHttpResponse:
    """Stream workspace events as Server-Sent Events.

    Login is enforced and the requested workspace must match the caller's
    own workspace so the stream is never a cross-tenant oracle.
    """
    user = await sync_to_async(getattr)(request, "user", None)
    if user is None or not await sync_to_async(getattr)(user, "is_authenticated", False):
        return StreamingHttpResponse(
            iter(["event: error\ndata: {\"detail\": \"Authentication required.\"}\n\n"]),
            content_type="text/event-stream",
            status=401,
        )
    profile = await sync_to_async(getattr)(user, "profile", None)
    caller_workspace = await sync_to_async(getattr)(profile, "workspace_id", None)
    if caller_workspace is not None and caller_workspace != workspace_id:
        return StreamingHttpResponse(
            iter(["event: error\ndata: {\"detail\": \"Forbidden workspace.\"}\n\n"]),
            content_type="text/event-stream",
            status=403,
        )

    response = StreamingHttpResponse(
        _event_stream(workspace_id), content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


# ---------------------------------------------------------------------------
# WebSocket consumer — same group, JSON transport
# ---------------------------------------------------------------------------


class WorkspaceEventConsumer(AsyncJsonWebsocketConsumer):
    """Relay a workspace group's events to one WebSocket connection."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.workspace_id: int | str | None = None
        self.group: str | None = None

    async def connect(self) -> None:
        user = self.scope.get("user")
        if user is None or not getattr(user, "is_authenticated", False):
            await self.close(code=4401)
            return
        try:
            self.workspace_id = self.scope["url_route"]["kwargs"]["workspace_id"]
        except (KeyError, TypeError):
            await self.close(code=4400)
            return
        # The reverse OneToOne ``profile`` is lazy; under a real daphne event
        # loop a synchronous access raises ``SynchronousOnlyOperation``, so
        # resolve it (and its workspace_id column) off the loop — mirroring the
        # SSE view's authorization path.
        profile = await sync_to_async(getattr)(user, "profile", None)
        caller_workspace = await sync_to_async(getattr)(profile, "workspace_id", None)
        if caller_workspace is not None and int(caller_workspace) != int(self.workspace_id):
            await self.close(code=4403)
            return
        self.group = workspace_group(self.workspace_id)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        if self.group is not None:
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def workspace_event(self, event: dict[str, Any]) -> None:
        """Receive a ``workspace.event`` group message and relay it."""
        await self.send_json({"event": event.get("event", "message"), "data": event.get("data", {})})
