"""End-to-end daphne smoke test for the realtime SSE road.

Connects a subscriber to the real ``workspace_events_sse`` streaming view,
runs a real tenant-scoped mutation, and asserts the typed event the mutation
publishes arrives on the stream — the same pipeline daphne serves in
production (``asgi.application`` → ``ProtocolTypeRouter`` → the SSE view → the
channel-layer group).

Why a single event loop + ``TransactionTestCase``
-------------------------------------------------
Under daphne one event loop drives everything, and the sync mutation views
publish through ``safe_publish_workspace_event`` →
``publish_workspace_event`` → ``async_to_sync(group_send)`` on a Redis channel
layer, which is cross-loop safe. The test environment has no Redis, so the
channel layer is ``InMemoryChannelLayer`` whose ``asyncio.Queue`` is not
cross-loop safe — a ``group_send`` issued on a different loop is not delivered
promptly. This test therefore runs the subscribe and publish steps in one loop
via ``apublish_workspace_event`` (the async form of the exact helper the
mutation views call) and uses ``TransactionTestCase`` so the ``setUp`` fixture
is committed and visible to the worker thread that performs the mutation
through ``sync_to_async``.
"""

from __future__ import annotations

import asyncio

from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.test import RequestFactory, TransactionTestCase

from apps.core.models import Workspace
from apps.core.realtime import apublish_workspace_event, workspace_events_sse
from apps.core.resources import create_row


def _flush_channel_layer() -> None:
    """Drop all channels/groups from the in-memory channel layer."""
    layer = get_channel_layer()
    if layer is not None and hasattr(layer, "flush"):
        async_to_sync(layer.flush)()


class DaphneSseSmokeTest(TransactionTestCase):
    def setUp(self):
        _flush_channel_layer()
        self.workspace = Workspace.objects.create(name="Smoke", slug="smoke")
        self.user = User.objects.create_user(
            username="smoke-member", email="smoke@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()

    def tearDown(self):
        _flush_channel_layer()
        super().tearDown()

    def _open_stream(self, workspace_pk):
        request = RequestFactory().get(f"/sse/workspace/{workspace_pk}/events/")
        request.user = self.user
        return request

    @staticmethod
    def _decode(chunk):
        return chunk.decode() if isinstance(chunk, bytes) else chunk

    def test_mutation_publishes_event_that_reaches_the_sse_stream(self):
        """Subscribe → real mutation → typed event delivered end-to-end."""
        workspace_pk = self.workspace.pk

        async def scenario():
            response = await workspace_events_sse(
                self._open_stream(workspace_pk), workspace_pk
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "text/event-stream")

            stream = response.streaming_content
            try:
                # The first frame is the SSE retry hint. It is yielded *after*
                # the group subscription, so by the time we read it the stream
                # is live and receiving group messages. Django encodes the
                # text/event-stream chunks to bytes, so decode before asserting.
                first = self._decode(await stream.__anext__())
                self.assertIn("retry: 3000", first)

                # A real, tenant-scoped mutation through the same service the
                # resource API uses for ``POST /api/v1/companies/``.
                row, errors, status = await sync_to_async(create_row)(
                    "companies", {"name": "Smoke Co"}, workspace_pk
                )
                self.assertEqual(status, 201, errors)

                # Publish exactly what ``resource_api`` publishes on create,
                # in its async form so it lands on this loop's in-memory layer.
                await apublish_workspace_event(
                    workspace_pk,
                    "resource.created",
                    {"resource": "companies", "row": row},
                )

                # The stream must deliver the typed event frame end-to-end.
                frame = self._decode(
                    await asyncio.wait_for(stream.__anext__(), timeout=5)
                )
                self.assertIn("event: resource.created", frame)
                self.assertIn('"resource": "companies"', frame)
                self.assertIn("Smoke Co", frame)
            finally:
                await stream.aclose()

        async_to_sync(scenario)()

    def test_event_published_to_another_workspace_does_not_leak(self):
        """A mutation in workspace B never reaches workspace A's stream."""
        other = Workspace.objects.create(name="Other", slug="other")

        async def scenario():
            response = await workspace_events_sse(
                self._open_stream(self.workspace.pk), self.workspace.pk
            )
            stream = response.streaming_content
            try:
                await stream.__anext__()  # consume the retry frame

                # Publish to the *other* workspace's group only.
                await apublish_workspace_event(
                    other.pk,
                    "resource.created",
                    {"resource": "companies", "row": {"id": 1, "name": "Leak"}},
                )

                # Our stream must not receive it; the 20s keep-alive is far
                # outside the wait, so this timeout proves non-delivery.
                with self.assertRaises(asyncio.TimeoutError):
                    await asyncio.wait_for(stream.__anext__(), timeout=0.5)
            finally:
                await stream.aclose()

        async_to_sync(scenario)()
