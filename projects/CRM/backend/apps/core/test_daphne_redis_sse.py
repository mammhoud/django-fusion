"""Redis-gated end-to-end smoke test: real daphne + HTTP/SSE over a socket.

This is the production-shape counterpart of ``test_sse_smoke.py``. That test
drives the SSE view in-process and publishes on one event loop because the dev
channel layer (``InMemoryChannelLayer``) is not cross-loop safe. Under a Redis
channel layer the sync mutation path
(``safe_publish_workspace_event`` → ``async_to_sync(group_send)``) is
cross-process safe, so this test boots a real daphne server in a subprocess,
opens a genuine HTTP connection, performs a real tenant-scoped mutation, and
asserts the published event arrives on the live SSE socket.

The class is skipped unless the active channel layer is Redis *and* the test
database is file-backed (set ``LOOP_TEST_DB_NAME=/path/to.sqlite3``). The
file-backed DB is required because the daphne subprocess must share the test
data, and the suite's default in-memory SQLite cannot cross a process boundary.
"""

from __future__ import annotations

import http.client
import unittest
from urllib.parse import urlparse

from channels.testing.live import ChannelsLiveServerTestCase
from django.conf import settings
from django.contrib.auth.models import User

from apps.core.models import Workspace
from apps.core.realtime import safe_publish_workspace_event
from apps.core.resources import create_row

_REDIS_ACTIVE = "redis" in settings.CHANNEL_LAYERS["default"]["BACKEND"].lower()


def _file_db_active() -> bool:
    test_name = settings.DATABASES["default"].get("TEST", {}).get("NAME")
    return bool(test_name) and ":memory:" not in str(test_name)


def _read_sse_frame(response: http.client.HTTPResponse) -> str:
    """Read one SSE frame (up to the terminating blank line)."""
    lines: list[str] = []
    while True:
        line = response.readline()
        if line == b"":
            if not lines:
                raise EOFError("SSE stream closed before any frame")
            break
        if line in (b"\n", b"\r\n"):
            break
        lines.append(line.decode("utf-8", "replace").rstrip("\r\n"))
    return "\n".join(lines)


@unittest.skipUnless(
    _REDIS_ACTIVE and _file_db_active(),
    "Requires a Redis channel layer and a file-based test DB (LOOP_TEST_DB_NAME)",
)
class DaphneRedisSseSmokeTest(ChannelsLiveServerTestCase):
    host = "127.0.0.1"
    serve_static = False

    def setUp(self):
        self.workspace = Workspace.objects.create(name="Daphne", slug="daphne")
        self.user = User.objects.create_user(
            username="daphne-member", email="d@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.client.force_login(self.user)
        self.session_cookie = f"sessionid={self.client.session.session_key}"

    def test_mutation_publishes_event_that_reaches_the_live_sse_stream(self):
        port = urlparse(self.live_server_url).port
        connection = http.client.HTTPConnection(self.host, port, timeout=8)
        try:
            connection.request(
                "GET",
                f"/sse/workspace/{self.workspace.pk}/events/",
                headers={"Cookie": self.session_cookie, "Accept": "text/event-stream"},
            )
            response = connection.getresponse()
            self.assertEqual(response.status, 200)

            # The first frame is the SSE retry hint — proves the stream is live
            # and the authenticated workspace group is subscribed.
            self.assertIn("retry: 3000", _read_sse_frame(response))

            # A real tenant-scoped mutation through the same service the
            # resource API uses, published through the real sync helper. Under
            # Redis this crosses processes and reaches daphne's event loop.
            row, errors, status = create_row("companies", {"name": "Daphne Co"}, self.workspace.pk)
            self.assertEqual(status, 201, errors)
            safe_publish_workspace_event(
                self.workspace.pk, "resource.created", {"resource": "companies", "row": row}
            )

            frame = _read_sse_frame(response)
            self.assertIn("event: resource.created", frame)
            self.assertIn('"resource": "companies"', frame)
            self.assertIn("Daphne Co", frame)
        finally:
            connection.close()
