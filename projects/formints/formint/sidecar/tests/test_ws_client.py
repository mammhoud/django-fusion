"""Tests for the POS terminal Cloud WebSocket sync client."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest

import ws_client
from ws_client import CloudSyncClient


class FakeWebSocket:
    """Minimal fake WebSocket for testing send/receive loops."""

    def __init__(self):
        self.sent: list[str] = []
        self.incoming: asyncio.Queue[str] = asyncio.Queue()

    async def send(self, data: str) -> None:
        self.sent.append(data)

    async def recv(self) -> str:
        return await self.incoming.get()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None


def _bind_client(client: CloudSyncClient) -> None:
    """Bind the client to the currently running event loop."""
    client._loop = asyncio.get_running_loop()
    if client._async_queue is None:
        client._async_queue = asyncio.Queue()


def test_publish_entity_event_queues_before_loop():
    """Messages are queued in memory before the event loop is started."""
    c = CloudSyncClient(url="ws://localhost/ws/sync-events/", branch_code="BR", node_id="N1")
    c.publish_entity_event("products", "create", {"id": 1, "name": "Coffee"})

    assert len(c._pending) == 1
    msg = c._pending.popleft()
    assert msg["type"] == "sync_push"
    payload = msg["payload"]
    assert payload["entity_type"] == "products"
    assert payload["action"] == "create"
    assert payload["data"]["name"] == "Coffee"
    assert payload["node_id"] == "N1"
    assert payload["branch_code"] == "BR"


@pytest.mark.asyncio
async def test_publish_entity_event_after_loop():
    """Messages are put on the async queue once the loop is available."""
    client = CloudSyncClient(
        url="ws://localhost/ws/sync-events/", branch_code="BR001", node_id="N1"
    )
    _bind_client(client)
    client.publish_entity_event("sales", "update", {"id": 2})
    await asyncio.sleep(0)  # let the loop process the thread-safe enqueue
    assert client._async_queue.qsize() == 1


@pytest.mark.asyncio
async def test_identify_message():
    """After connecting the client sends an identify message."""
    client = CloudSyncClient(
        url="ws://localhost/ws/sync-events/", branch_code="BR001", node_id="solo-node-1"
    )
    fake = FakeWebSocket()
    await client._identify(fake)

    assert len(fake.sent) == 1
    msg = json.loads(fake.sent[0])
    assert msg["type"] == "identify"
    assert msg["payload"]["branch_code"] == "BR001"
    assert msg["payload"]["node_id"] == "solo-node-1"


@pytest.mark.asyncio
async def test_sender_drains_async_queue():
    """The sender coroutine writes queued messages to the WebSocket."""
    client = CloudSyncClient(
        url="ws://localhost/ws/sync-events/", branch_code="BR001", node_id="N1"
    )
    _bind_client(client)
    fake = FakeWebSocket()
    client._async_queue.put_nowait({"type": "sync_push", "payload": {"x": 1}})

    # The sender blocks on the queue forever; cancel after it sends one message.
    task = asyncio.create_task(client._sender(fake))
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert len(fake.sent) == 1
    assert json.loads(fake.sent[0])["type"] == "sync_push"


@pytest.mark.asyncio
async def test_receiver_handles_entity_event():
    """Incoming broker messages with entity_event are broadcast locally."""
    client = CloudSyncClient(
        url="ws://localhost/ws/sync-events/", branch_code="BR001", node_id="N1"
    )
    _bind_client(client)
    fake = FakeWebSocket()
    payload = {
        "type": "broker_message",
        "message": {
            "subtype": "entity_event",
            "payload": {
                "entity_type": "products",
                "action": "update",
                "data": {"id": 7, "name": "Mocha"},
            },
        },
    }
    await fake.incoming.put(json.dumps(payload))

    with patch.object(ws_client.CloudSyncClient, "_broadcast_local", new=AsyncMock()) as mock_broadcast:
        task = asyncio.create_task(client._receiver(fake))
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    mock_broadcast.assert_awaited_once_with(
        "products", "update", {"id": 7, "name": "Mocha"}
    )


@pytest.mark.asyncio
async def test_receiver_handles_sync_event():
    """Incoming sync_event messages are broadcast locally."""
    client = CloudSyncClient(
        url="ws://localhost/ws/sync-events/", branch_code="BR001", node_id="N1"
    )
    _bind_client(client)
    fake = FakeWebSocket()
    await fake.incoming.put(json.dumps({
        "type": "sync_event",
        "data": {"entity_type": "sales", "synced": 3, "branch": "BR001"},
    }))

    with patch.object(ws_client.CloudSyncClient, "_broadcast_local", new=AsyncMock()) as mock_broadcast:
        task = asyncio.create_task(client._receiver(fake))
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    mock_broadcast.assert_awaited_once_with(
        "sales", "sync_event", {"entity_type": "sales", "synced": 3, "branch": "BR001"}
    )


@pytest.mark.asyncio
async def test_reconnect_backoff():
    """Failed connection attempts increase the reconnect backoff."""
    client = CloudSyncClient(url="ws://localhost/ws/", branch_code="BR", node_id="N")
    client._max_backoff = 8
    _bind_client(client)

    called: list[str] = []

    async def failing_connect():
        called.append("connect")
        raise ConnectionError("boom")

    client._connect_and_serve = failing_connect  # type: ignore[assignment]

    task = asyncio.create_task(client._run())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert client._attempts == 1
    assert len(called) == 1


@pytest.mark.asyncio
async def test_offline_queue_bound():
    """The offline queue drops oldest messages once it exceeds its max size."""
    client = CloudSyncClient(url="ws://localhost/ws/", branch_code="BR", node_id="N")
    original_max = CloudSyncClient.MAX_OFFLINE_QUEUE_SIZE
    try:
        CloudSyncClient.MAX_OFFLINE_QUEUE_SIZE = 2
        _bind_client(client)

        client.publish_entity_event("products", "create", {"id": 1})
        client.publish_entity_event("products", "create", {"id": 2})
        client.publish_entity_event("products", "create", {"id": 3})
        await asyncio.sleep(0)  # process thread-safe enqueues

        assert client._async_queue.qsize() == 2
        ids = [client._async_queue.get_nowait()["payload"]["data"]["id"] for _ in range(2)]
        # Oldest message (id=1) was dropped when id=3 was enqueued.
        assert ids == [2, 3]
    finally:
        CloudSyncClient.MAX_OFFLINE_QUEUE_SIZE = original_max


@pytest.mark.asyncio
async def test_receiver_skips_own_echo():
    """Messages originating from this node should not be re-broadcast locally."""
    client = CloudSyncClient(
        url="ws://localhost/ws/sync-events/", branch_code="BR001", node_id="echo-node"
    )
    _bind_client(client)
    fake = FakeWebSocket()
    await fake.incoming.put(json.dumps({
        "type": "broker_message",
        "message": {
            "subtype": "entity_event",
            "payload": {
                "entity_type": "products",
                "action": "update",
                "origin_node_id": "echo-node",
                "data": {"id": 1},
            },
        },
    }))

    with patch.object(ws_client.CloudSyncClient, "_broadcast_local", new=AsyncMock()) as mock_broadcast:
        task = asyncio.create_task(client._receiver(fake))
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    mock_broadcast.assert_not_awaited()


@pytest.mark.asyncio
async def test_receiver_falls_back_when_data_missing():
    """If the cloud payload has no data key, the whole payload is broadcast."""
    client = CloudSyncClient(
        url="ws://localhost/ws/sync-events/", branch_code="BR001", node_id="N1"
    )
    _bind_client(client)
    fake = FakeWebSocket()
    await fake.incoming.put(json.dumps({
        "type": "broker_message",
        "message": {
            "subtype": "entity_event",
            "payload": {
                "entity_type": "sales",
                "action": "sync",
                "count": 5,
            },
        },
    }))

    with patch.object(ws_client.CloudSyncClient, "_broadcast_local", new=AsyncMock()) as mock_broadcast:
        task = asyncio.create_task(client._receiver(fake))
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    mock_broadcast.assert_awaited_once_with(
        "sales", "sync", {"entity_type": "sales", "action": "sync", "count": 5}
    )
