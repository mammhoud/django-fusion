"""
POS Terminal — Cloud WebSocket Sync Client.

Background asyncio client that keeps a persistent WebSocket connection to the
POS Cloud CRM (``/ws/sync-events/``). It:

* identifies the terminal with ``branch_code`` + ``node_id``
* sends local entity CRUD events to the cloud (sync_push)
* receives cloud-to-terminal events and broadcasts them to local WebSocket
  clients (Redux/RTK Query cache invalidation)
* reconnects with exponential backoff and queues outbound messages while offline

Environment variables
---------------------
``POS_CLOUD_WS_URL``      Full WebSocket URL (optional; derived from ``CLOUD_CRM_URL``).
``POS_BRANCH_CODE``       Branch code registered in POS Cloud.
``POS_NODE_ID``           Unique node identifier for this terminal.
``POS_CLOUD_API_KEY``     Optional API key for cloud authentication.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import socket
import threading
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any

from asgiref.sync import sync_to_async

from streams import _broadcast_entity_event

logger = logging.getLogger("pos.ws_client")

# websockets is an optional runtime dependency; if missing the client is disabled.
try:
    import websockets
    from websockets.exceptions import ConnectionClosed
except ImportError:  # pragma: no cover
    websockets = None  # type: ignore
    ConnectionClosed = Exception  # type: ignore[assignment,misc]


# ── Environment helpers ─────────────────────────────────────────────────

def _default_node_id() -> str:
    """Generate a fallback node id from hostname."""
    return f"pos-solo-{socket.gethostname()}"


def _build_ws_url() -> str:
    """Build WebSocket URL from CLOUD_CRM_URL or env override."""
    url = os.environ.get("POS_CLOUD_WS_URL", "").strip()
    if url:
        return url

    base = os.environ.get("CLOUD_CRM_URL", "").strip().rstrip("/")
    if not base:
        return ""

    if base.startswith("http://"):
        base = "ws://" + base[7:]
    elif base.startswith("https://"):
        base = "wss://" + base[8:]
    elif base.startswith("ws://") or base.startswith("wss://"):
        pass
    else:
        base = f"ws://{base}"

    return f"{base}/ws/sync-events/"


# ── CloudSyncClient ─────────────────────────────────────────────────────

class CloudSyncClient:
    """Persistent WebSocket client for bidirectional POSCloud sync."""

    # Entity types that are worth pushing to the cloud in real time.
    # Maps Django model_name -> human entity name used in messages.
    # Child models (e.g. SaleItem) are intentionally omitted to avoid
    # duplicate events; the parent model (Sale) already covers them.
    SYNCED_ENTITIES = {
        "product": "products",
        "category": "products",
        "customer": "customers",
        "sale": "sales",
        "inventorytransaction": "inventory",
        "menu": "menu_items",
        "employee": "employees",
    }

    # Maximum number of outbound messages kept while offline.
    MAX_OFFLINE_QUEUE_SIZE = 1000

    def __init__(
        self,
        url: str | None = None,
        branch_code: str | None = None,
        node_id: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.url = url or _build_ws_url()
        self.branch_code = (branch_code or os.environ.get("POS_BRANCH_CODE", "DEFAULT")).strip()
        self.node_id = (node_id or os.environ.get("POS_NODE_ID", _default_node_id())).strip()
        self.api_key = api_key or os.environ.get("POS_CLOUD_API_KEY", "")

        self._loop: asyncio.AbstractEventLoop | None = None
        self._task: asyncio.Task | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._connected = False
        self._attempts = 0
        self._max_backoff = 60

        # Thread-safe pre-start queue; drained once the event loop is running.
        self._pending: deque[dict] = deque()
        self._async_queue: asyncio.Queue[dict] | None = None

    @staticmethod
    def _bounded_put(queue: asyncio.Queue[dict], item: dict, max_size: int) -> None:
        """Put an item into an async queue, dropping oldest if over the limit."""
        while queue.qsize() >= max_size:
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        queue.put_nowait(item)

    # ── Public API ──────────────────────────────────────────────────────

    def start(self) -> None:
        """Start the background WebSocket client thread."""
        if self._thread is not None and self._thread.is_alive():
            return
        if websockets is None:
            logger.warning("websockets package not installed; real-time sync disabled")
            return
        if not self.url:
            logger.info("No cloud WebSocket URL configured; real-time sync disabled")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_thread, daemon=True, name="cloud-ws-client")
        self._thread.start()
        logger.info("Cloud WebSocket sync client started (branch=%s node=%s)", self.branch_code, self.node_id)

    def stop(self) -> None:
        """Signal the client to stop and wait briefly for the thread."""
        self._stop_event.set()
        if self._task and self._loop:
            self._loop.call_soon_threadsafe(self._task.cancel)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def publish_entity_event(self, entity: str, action: str, data: dict) -> None:
        """Queue a local entity change to be sent to the cloud.

        Safe to call from any thread (including Django signal handlers).
        """
        if not self.url:
            return

        message = {
            "type": "sync_push",
            "payload": {
                "entity_type": entity,
                "action": action,
                "node_id": self.node_id,
                "branch_code": self.branch_code,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data,
                "count": 1,
            },
        }

        if self._loop and self._loop.is_running() and self._async_queue is not None:
            self._loop.call_soon_threadsafe(
                self._bounded_put, self._async_queue, message, self.MAX_OFFLINE_QUEUE_SIZE
            )
        else:
            while len(self._pending) >= self.MAX_OFFLINE_QUEUE_SIZE:
                self._pending.popleft()
            self._pending.append(message)

    # ── Internal event loop entry ───────────────────────────────────────

    def _run_thread(self) -> None:
        """Thread target: create an event loop and run the client coroutine."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        self._async_queue = asyncio.Queue()

        # Drain pre-start messages
        while self._pending:
            loop.call_soon(self._async_queue.put_nowait, self._pending.popleft())

        try:
            self._task = loop.create_task(self._run())
            loop.run_until_complete(self._task)
        except asyncio.CancelledError:
            pass
        finally:
            loop.close()
            self._loop = None
            self._async_queue = None

    # ── Connection lifecycle ────────────────────────────────────────────

    async def _run(self) -> None:
        """Main reconnection loop."""
        while not self._stop_event.is_set():
            try:
                await self._connect_and_serve()
                self._attempts = 0
            except Exception as exc:  # pragma: no cover
                logger.warning("WebSocket client error: %s", exc)

            self._connected = False
            if self._stop_event.is_set():
                break

            self._attempts += 1
            delay = min(2 ** self._attempts, self._max_backoff)
            logger.info("Reconnecting to cloud WebSocket in %ss...", delay)
            await asyncio.sleep(delay)

    async def _connect_and_serve(self) -> None:
        """Connect, identify, then run send/receive loops."""
        self._attempts = 0
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        logger.info("Connecting to cloud WebSocket: %s", self.url)
        async with websockets.connect(self.url, extra_headers=headers) as ws:  # type: ignore[arg-type]
            self._connected = True
            self._attempts = 0
            logger.info("Connected to cloud WebSocket")

            await self._identify(ws)

            sender = asyncio.create_task(self._sender(ws), name="ws-sender")
            receiver = asyncio.create_task(self._receiver(ws), name="ws-receiver")

            try:
                await asyncio.gather(sender, receiver)
            finally:
                sender.cancel()
                receiver.cancel()
                try:
                    await asyncio.gather(sender, receiver, return_exceptions=True)
                except Exception:
                    pass

    async def _identify(self, ws) -> None:
        identify = {
            "type": "identify",
            "payload": {
                "branch_code": self.branch_code,
                "node_id": self.node_id,
            },
        }
        await ws.send(json.dumps(identify))

    # ── Sender / receiver ───────────────────────────────────────────────

    async def _sender(self, ws) -> None:
        """Send queued outbound messages."""
        while True:
            try:
                message = await asyncio.wait_for(self._async_queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            try:
                await ws.send(json.dumps(message))
                logger.debug("Sent to cloud: %s", message.get("type"))
            except Exception as exc:
                logger.warning("Failed to send WebSocket message: %s", exc)
                # Re-queue the message for the next connection
                self._loop.call_soon_threadsafe(self._async_queue.put_nowait, message)
                break

    async def _receiver(self, ws) -> None:
        """Receive messages from the cloud and dispatch them."""
        while True:
            try:
                raw = await ws.recv()
            except ConnectionClosed:
                logger.info("Cloud WebSocket connection closed")
                break

            if not isinstance(raw, str):
                continue
            await self._handle_message(raw)

    # ── Message dispatch ────────────────────────────────────────────────

    def _is_own_echo(self, message: dict) -> bool:
        """Return True if this message originated from this terminal."""
        if message.get("origin_node_id") == self.node_id:
            return True
        payload = message.get("payload")
        if isinstance(payload, dict) and payload.get("origin_node_id") == self.node_id:
            return True
        return False

    async def _handle_message(self, raw: str) -> None:
        """Route an incoming cloud message to the appropriate handler."""
        try:
            message = json.loads(raw)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            logger.warning("Invalid message from cloud: %s", exc)
            return

        if self._is_own_echo(message):
            return

        msg_type = message.get("type", "")

        if msg_type == "identify_ack":
            logger.info("Cloud acknowledged identity: %s", message)
            return

        if msg_type == "error":
            logger.warning("Cloud error: %s", message)
            return

        if msg_type == "sync_event":
            await self._handle_sync_event(message.get("data", {}))
            return

        if msg_type == "broker_message":
            await self._handle_broker_message(message.get("message", {}))
            return

        logger.debug("Unhandled cloud message type: %s", msg_type)

    async def _handle_sync_event(self, data: dict) -> None:
        """Forward a cloud sync_event to local WebSocket listeners."""
        entity = data.get("entity_type", "unknown")
        await self._broadcast_local(entity, "sync_event", data)

    async def _handle_broker_message(self, data: dict) -> None:
        """Forward a broker message to local WebSocket listeners."""
        subtype = data.get("subtype", "")
        payload = data.get("payload", {})

        if subtype == "entity_event":
            entity = payload.get("entity_type", "unknown")
            await self._broadcast_local(
                entity, payload.get("action", "update"), payload.get("data", payload),
            )
        else:
            # Generic broker message — still broadcast so UI can react.
            await self._broadcast_local("broker", subtype, data)

    async def _broadcast_local(self, entity: str, action: str, data: dict) -> None:
        """Broadcast to local entity WebSocket clients (Redux/RTK cache refresh)."""
        try:
            await _broadcast_entity_event(entity, action, data)
        except Exception as exc:
            logger.warning("Failed to broadcast local entity event: %s", exc)


# ── Singleton ───────────────────────────────────────────────────────────

cloud_ws_client = CloudSyncClient()


def publish_entity_event(entity: str, action: str, data: dict) -> None:
    """Convenience wrapper used by signal handlers."""
    cloud_ws_client.publish_entity_event(entity, action, data)


def start_client() -> None:
    """Start the global WebSocket sync client."""
    cloud_ws_client.start()


def stop_client() -> None:
    """Stop the global WebSocket sync client."""
    cloud_ws_client.stop()
