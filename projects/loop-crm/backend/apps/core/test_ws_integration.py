"""Channels WebSocket integration test for the realtime workspace consumer.

Drives the real ``WorkspaceEventConsumer`` through ``URLRouter`` (the exact
route table ``asgi.py`` mounts) using ``channels.testing.WebsocketCommunicator``
and the in-memory channel layer, asserting:

* a published mutation reaches a connected member of the workspace, and
* a member is rejected when connecting to another workspace's stream
  (close code 4403), and
* a mutation published to another workspace never leaks to this member.

Auth + loop notes
-----------------
The consumer authorizes the workspace itself (close 4403 on mismatch) after
``AuthMiddlewareStack`` has resolved ``scope["user"]``. This test injects the
authenticated user into the scope directly — the same pattern as formints'
``test_ws_parity_contract.py`` — so the consumer's authorization + relay path
is exercised deterministically without session-cookie plumbing. Session→user
resolution is already covered by the SSE smoke test and the
``workspace/current`` auth test.

Like the SSE smoke test, subscribe + publish run on a single event loop via
``apublish_workspace_event`` (the async form of the helper the mutation views
call), and ``TransactionTestCase`` is used so fixture rows are committed and
visible to the ``sync_to_async`` worker thread. Both are required because the
CI environment has no Redis and ``InMemoryChannelLayer``'s queue is not
cross-loop safe; under a Redis layer the sync and async publish forms are
interchangeable.
"""

from __future__ import annotations

import asyncio

from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.test import TransactionTestCase

from apps.core.models import Workspace
from apps.core.realtime import apublish_workspace_event
from apps.core.resources import create_row
from apps.core.routing import websocket_urlpatterns


def _flush_channel_layer() -> None:
    """Drop all channels/groups from the in-memory channel layer."""
    layer = get_channel_layer()
    if layer is not None and hasattr(layer, "flush"):
        async_to_sync(layer.flush)()


class WorkspaceWebSocketIntegrationTest(TransactionTestCase):
    def setUp(self):
        _flush_channel_layer()
        self.workspace = Workspace.objects.create(name="WS Smoke", slug="ws-smoke")
        self.other = Workspace.objects.create(name="WS Other", slug="ws-other")
        self.user = User.objects.create_user(
            username="ws-member", email="ws@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()

    def tearDown(self):
        _flush_channel_layer()
        super().tearDown()

    def _communicator(self, workspace_pk) -> WebsocketCommunicator:
        communicator = WebsocketCommunicator(
            URLRouter(websocket_urlpatterns), f"/ws/workspace/{workspace_pk}/"
        )
        # The consumer authorizes from scope["user"] (set by AuthMiddlewareStack
        # in production); inject the authenticated member for determinism.
        communicator.scope["user"] = self.user
        return communicator

    @staticmethod
    async def _disconnect(communicator: WebsocketCommunicator) -> None:
        # A timed-out receive cancels the application task; disconnect() then
        # re-raises the cancellation when it reaps the future. Best-effort
        # teardown is fine — the channel layer is flushed between tests.
        try:
            await communicator.disconnect()
        except (asyncio.CancelledError, asyncio.TimeoutError, ValueError):
            pass

    async def test_published_mutation_reaches_connected_member(self):
        comm = self._communicator(self.workspace.pk)
        connected, _subprotocol = await comm.connect()
        self.assertTrue(connected, "member must connect to their own workspace")
        try:
            # A real tenant-scoped mutation through the same service the
            # resource API uses for ``POST /api/v1/companies/``.
            row, errors, status = await sync_to_async(create_row)(
                "companies", {"name": "WS Co"}, self.workspace.pk
            )
            self.assertEqual(status, 201, errors)

            # Publish exactly what ``resource_api`` publishes on create, in its
            # async form so it lands on this loop's in-memory channel layer.
            await apublish_workspace_event(
                self.workspace.pk,
                "resource.created",
                {"resource": "companies", "row": row},
            )

            frame = await comm.receive_json_from(timeout=5)
            self.assertEqual(frame["event"], "resource.created")
            self.assertEqual(frame["data"]["resource"], "companies")
            self.assertEqual(frame["data"]["row"]["name"], "WS Co")
        finally:
            await self._disconnect(comm)

    async def test_cross_tenant_connection_is_rejected(self):
        comm = self._communicator(self.other.pk)
        connected, close_code = await comm.connect()
        self.assertFalse(connected, "member must not connect to another workspace")
        self.assertEqual(close_code, 4403)
        await self._disconnect(comm)

    async def test_mutation_in_another_workspace_does_not_leak(self):
        comm = self._communicator(self.workspace.pk)
        connected, _subprotocol = await comm.connect()
        self.assertTrue(connected, "member must connect to their own workspace")
        try:
            await apublish_workspace_event(
                self.other.pk,
                "resource.created",
                {"resource": "companies", "row": {"id": 1, "name": "Leak"}},
            )
            # The member's socket must stay silent; the timeout proves the
            # other workspace's group was never joined.
            with self.assertRaises(asyncio.TimeoutError):
                await comm.receive_json_from(timeout=0.5)
        finally:
            await self._disconnect(comm)
