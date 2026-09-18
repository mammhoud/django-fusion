"""Redis-gated end-to-end WebSocket smoke test: real daphne + a live consumer.

This is the WebSocket counterpart of ``test_daphne_redis_sse.py``. That test
boots a real daphne server and drives HTTP/SSE over a socket; this one opens a
real RFC 6455 WebSocket to the ``WorkspaceEventConsumer`` the same daphne
process serves, runs a tenant-scoped mutation, publishes through the sync
helper, and asserts the typed ``{event, data}`` frame reaches the open socket.

The class is skipped unless the active channel layer is Redis *and* the test
database is file-backed (set ``LOOP_TEST_DB_NAME=/path/to.sqlite3``). The
file-backed DB is required because the daphne subprocess must share the test
data, and the suite's default in-memory SQLite cannot cross a process
boundary.
"""

from __future__ import annotations

import base64
import json
import os
import socket
import struct
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

# RFC 6455 opcode for a single text frame (the consumer's ``send_json`` output).
_TEXT_OPCODE = 0x1


class _RawWebSocket:
    """Minimal RFC 6455 client (stdlib only) — handshake + unmasked frame reads.

    The consumer only ever sends server frames (unmasked, per RFC 6455), so the
    client needs no frame-masking on the read path and sends nothing after the
    handshake.
    """

    def __init__(self, host: str, port: int, path: str, cookie: str | None = None):
        self.sock = socket.create_connection((host, port), timeout=8)
        self._buf = b""
        self.status = self._handshake(host, port, path, cookie)

    def _handshake(self, host: str, port: int, path: str, cookie: str | None) -> int:
        key = base64.b64encode(os.urandom(16)).decode()
        lines = [
            f"GET {path} HTTP/1.1",
            f"Host: {host}:{port}",
            "Upgrade: websocket",
            "Connection: Upgrade",
            f"Sec-WebSocket-Key: {key}",
            "Sec-WebSocket-Version: 13",
        ]
        if cookie:
            lines.append(f"Cookie: {cookie}")
        self.sock.sendall(("\r\n".join(lines) + "\r\n\r\n").encode("latin1"))
        head = self._read_until(b"\r\n\r\n")
        status_line = head.split(b"\r\n", 1)[0].decode("latin1")
        return int(status_line.split(" ", 2)[1])

    def _read_until(self, marker: bytes) -> bytes:
        while marker not in self._buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError("WebSocket closed before the marker arrived")
            self._buf += chunk
        head, _, rest = self._buf.partition(marker)
        self._buf = rest
        return head

    def _recv_exact(self, n: int) -> bytes:
        while len(self._buf) < n:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError("WebSocket closed mid-frame")
            self._buf += chunk
        out = self._buf[:n]
        self._buf = self._buf[n:]
        return out

    def recv_frame(self) -> tuple[int, bytes]:
        """Return ``(opcode, payload)`` for one unmasked server frame."""
        b0, b1 = self._recv_exact(2)
        opcode = b0 & 0x0F
        length = b1 & 0x7F
        if length == 126:
            length = struct.unpack(">H", self._recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self._recv_exact(8))[0]
        return opcode, self._recv_exact(length)

    def close(self) -> None:
        self.sock.close()


@unittest.skipUnless(
    _REDIS_ACTIVE and _file_db_active(),
    "Requires a Redis channel layer and a file-based test DB (LOOP_TEST_DB_NAME)",
)
class DaphneRedisWebSocketSmokeTest(ChannelsLiveServerTestCase):
    host = "127.0.0.1"
    serve_static = False

    def setUp(self):
        self.workspace = Workspace.objects.create(name="Daphne WS", slug="daphne-ws")
        self.user = User.objects.create_user(
            username="daphne-ws-member", email="dws@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.client.force_login(self.user)
        self.session_cookie = f"sessionid={self.client.session.session_key}"

    def test_mutation_reaches_the_open_consumer(self):
        port = urlparse(self.live_server_url).port
        ws = _RawWebSocket(
            self.host, port, f"/ws/workspace/{self.workspace.pk}/", self.session_cookie
        )
        try:
            self.assertEqual(ws.status, 101, "WebSocket upgrade must succeed")

            # A real tenant-scoped mutation through the same service the
            # resource API uses, published through the real sync helper. Under
            # Redis this crosses processes and reaches daphne's event loop.
            row, errors, status = create_row(
                "companies", {"name": "Daphne WS Co"}, self.workspace.pk
            )
            self.assertEqual(status, 201, errors)

            safe_publish_workspace_event(
                self.workspace.pk,
                "resource.created",
                {"resource": "companies", "row": row},
            )

            ws.sock.settimeout(8)
            opcode, payload = ws.recv_frame()
            self.assertEqual(opcode, _TEXT_OPCODE, "consumer must send a text frame")
            frame = json.loads(payload.decode("utf-8"))
            self.assertEqual(frame["event"], "resource.created")
            self.assertEqual(frame["data"]["resource"], "companies")
            self.assertEqual(frame["data"]["row"]["name"], "Daphne WS Co")
        finally:
            ws.close()
