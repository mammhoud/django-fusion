"""POS Cloud — Redis-gated smoke tests for the two broker roads.

Formint Cloud has two distinct "broker" paths that only behave differently
from their in-process stand-ins when a real Redis server is present:

1. **Dramatiq task broker** — ``django_fusion.tasks`` wires the ``@task``
   decorators (``backup_db``, ``process_sync_queue``) onto a
   ``dramatiq.brokers.redis.RedisBroker``. With no Redis the backend still
   configures, but ``.send()`` would fail; these tests prove a task enqueue
   actually lands a message in Redis.

2. **WebSocket sync broker** — ``apps.domain.sync_broker.SyncBroker`` pushes
   ``BrokerMessage`` frames onto the Channels layer. The in-memory layer
   (``test_ws_sync_events.py``) only works within one event loop; these tests
   prove ``push_to_branch`` delivers over a real ``RedisChannelLayer``.

Both classes are ``skipUnless``-gated on a live Redis at the configured URL
(``REDIS_URL`` / ``REDIS_HOST`` / ``REDIS_PORT`` / ``REDIS_PASSWORD``), so the
default unit suite stays fast and green without Redis. Run them with::

    REDIS_URL=redis://127.0.0.1:6379 manage.py test apps.test_redis_broker_smoke
"""

from __future__ import annotations

import unittest

from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.test import TransactionTestCase

from apps.core.models import Branch, Organization
from apps.domain.sync_broker import BrokerMessage, broker
from apps.handlers.consumers import SyncEventConsumer


def _broker_url() -> str:
    """The configured Dramatiq broker URL (same one the task registry uses)."""
    return settings.FUSION_TASKS.get("BROKER_URL", "redis://127.0.0.1:6379/1")


def _redis_up() -> bool:
    """True when a real Redis server answers at the configured URL."""
    try:
        import redis

        return bool(
            redis.Redis.from_url(
                _broker_url(),
                socket_connect_timeout=1.0,
                socket_timeout=1.0,
            ).ping()
        )
    except Exception:
        return False


def _channel_layer_is_redis() -> bool:
    backend = settings.CHANNEL_LAYERS["default"]["BACKEND"].lower()
    return "redis" in backend


def _flush_channel_layer() -> None:
    """Drop all channels/groups so tests never leak state to each other."""
    layer = get_channel_layer()
    if layer is not None and hasattr(layer, "flush"):
        async_to_sync(layer.flush)()


@unittest.skipUnless(_redis_up(), "Requires a live Redis broker (REDIS_URL)")
class DramatiqBrokerRedisSmokeTest(TransactionTestCase):
    """The Dramatiq task road — enqueue must persist into Redis."""

    def test_task_backend_is_redis_backed(self):
        """The django-fusion registry resolves to a real RedisBroker."""
        from django_fusion.tasks.registry import task_registry

        backend = task_registry.backend
        self.assertIsNotNone(backend, "Task registry has no configured backend")
        self.assertIsNotNone(backend.broker, "Dramatiq broker should be constructed")
        self.assertEqual(backend.broker.namespace, "dramatiq")

    def test_task_enqueue_lands_a_message_in_redis(self):
        """``run_backup.send()`` must store a message in the ``system`` queue."""
        from django_fusion.tasks.registry import task_registry
        from plugins.workers.backup_tasks import run_backup

        backend = task_registry.backend
        broker_obj = backend.broker
        self.assertIsNotNone(broker_obj)

        # flush any prior message so the assertion is about *this* enqueue
        broker_obj.flush("system")

        message_id = run_backup.send()
        self.assertTrue(message_id, "enqueue should return a Dramatiq message id")

        # The message must be physically present under the dramatiq namespace —
        # not just acknowledged by an in-process stub. dramatiq stores the queue
        # as a LIST of message ids (`dramatiq:system`) plus a HASH of payloads
        # (`dramatiq:system.msgs`). Note the hash is keyed by dramatiq's
        # per-attempt ``redis_message_id`` (unique across retries), not the
        # logical ``message_id`` returned by ``send()`` — so assert the returned
        # id appears inside the encoded payload rather than as the hash key.
        queue_key = f"{broker_obj.namespace}:system"
        msgs_key = f"{queue_key}.msgs"
        self.assertGreaterEqual(
            broker_obj.client.llen(queue_key),
            1,
            f"expected >=1 message on Redis queue {queue_key!r}",
        )
        payloads = broker_obj.client.hvals(msgs_key)
        self.assertGreaterEqual(
            len(payloads),
            1,
            f"expected the message payload in Redis hash {msgs_key!r}",
        )
        self.assertTrue(
            any(message_id.encode() in payload for payload in payloads),
            f"enqueued payload for {message_id!r} should be in {msgs_key!r}",
        )

        # Clean up so repeated runs are deterministic.
        broker_obj.flush("system")


@unittest.skipUnless(
    _redis_up() and _channel_layer_is_redis(),
    "Requires a live Redis channel layer (REDIS_URL / REDIS_HOST)",
)
class SyncBrokerRedisSmokeTest(TransactionTestCase):
    """The WebSocket sync-broker road — push_to_branch over Redis."""

    def setUp(self):
        self.org = Organization.objects.create(name="Redis Org", slug="redis-org")
        self.branch = Branch.objects.create(
            organization=self.org, name="Redis Branch", code="RED001",
        )
        _flush_channel_layer()
        broker.reset()

    def tearDown(self):
        broker.reset()
        _flush_channel_layer()
        super().tearDown()

    async def test_push_to_branch_delivers_over_redis(self):
        """A branch push travels the Redis channel layer to the client."""
        comm = WebsocketCommunicator(
            SyncEventConsumer.as_asgi(), "/ws/sync-events/"
        )
        connected, _ = await comm.connect()
        self.assertTrue(connected, "WebSocket connect should succeed")

        try:
            await comm.send_json_to({
                "type": "identify",
                "payload": {"branch_code": "RED001", "node_id": "node-redis-1"},
            })
            ack = await comm.receive_json_from(timeout=5)
            self.assertEqual(ack["type"], "identify_ack")

            message = BrokerMessage(
                type="entity_event",
                payload={"entity_type": "products", "action": "sync", "count": 7},
            )
            # This is the real production push path. ``push_to_branch`` is the
            # sync service that calls ``async_to_sync(group_send)``; because the
            # test body is async (we ``await`` the communicator), run it in a
            # thread via ``sync_to_async`` so ``async_to_sync`` can spin up its
            # own event loop — the same shape as a sync Django view.
            accepted = await sync_to_async(broker.push_to_branch)("RED001", message)
            self.assertTrue(accepted, "push_to_branch should accept over Redis")

            frame = await comm.receive_json_from(timeout=5)
            self.assertEqual(frame["type"], "broker_message")
            self.assertEqual(frame["message"]["subtype"], "entity_event")
            self.assertEqual(frame["message"]["payload"]["count"], 7)
        finally:
            await comm.disconnect()
