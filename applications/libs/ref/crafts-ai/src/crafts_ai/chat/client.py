"""
crafts_ai.chat.client
======================

REST API client and chat bubble interface for the crafts-ai server.

Classes
-------
CraftsClient
    Low-level HTTP client for the crafts-ai REST API.
ChatBubble
    High-level chat interface — send a message, get a reply.
ChatMessage
    Simple dataclass representing a chat message.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """A single chat message."""

    text: str
    role: str = "assistant"  # "user" | "assistant"
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CraftsClient:
    """
    Low-level REST client for the crafts-ai server.

    Uses only the Python standard library (urllib) — no requests dependency.

    Args:
        base_url: Base URL of the crafts-ai server (e.g. ``"http://localhost:8765"``).
        timeout: Request timeout in seconds (default 30).
        headers: Extra HTTP headers to include in every request.

    Usage::

        client = CraftsClient(base_url="http://localhost:8765")
        data = client.post("/chat", {"message": "Hello", "session_id": "abc"})
        print(data["reply"])
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8765",
        timeout: int = 30,
        headers: Dict[str, str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if headers:
            self.default_headers.update(headers)

    def _request(
        self,
        method: str,
        path: str,
        data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request and return parsed JSON."""
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode("utf-8") if data else None

        req = urllib.request.Request(
            url,
            data=body,
            headers=self.default_headers,
            method=method.upper(),
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8") if exc.fp else ""
            logger.error("CraftsClient HTTP %s %s → %d: %s", method, url, exc.code, raw)
            raise
        except urllib.error.URLError as exc:
            logger.error("CraftsClient connection error %s %s: %s", method, url, exc.reason)
            raise

    def get(self, path: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """Send a GET request."""
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            path = f"{path}?{query}"
        return self._request("GET", path)

    def post(self, path: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a POST request with JSON body."""
        return self._request("POST", path, data)

    def health(self) -> bool:
        """Return True if the server is reachable and healthy."""
        try:
            resp = self.get("/health")
            return resp.get("status") == "ok"
        except Exception:
            return False


class ChatBubble:
    """
    High-level chat interface for the crafts-ai server.

    Maintains a session and provides a simple ``send()`` / ``history`` API.

    Args:
        server_url: Base URL of the crafts-ai server.
        session_id: Optional session identifier (auto-generated if omitted).
        timeout: Request timeout in seconds.

    Usage::

        bubble = ChatBubble(server_url="http://localhost:8765")
        reply = bubble.send("Hello, what can you help me with?")
        print(reply.text)

        for msg in bubble.history:
            print(f"[{msg.role}] {msg.text}")
    """

    def __init__(
        self,
        server_url: str = "http://localhost:8765",
        session_id: Optional[str] = None,
        timeout: int = 30,
    ):
        import uuid
        self.client = CraftsClient(base_url=server_url, timeout=timeout)
        self.session_id = session_id or str(uuid.uuid4())
        self._history: List[ChatMessage] = []

    @property
    def history(self) -> List[ChatMessage]:
        """Return the full conversation history."""
        return list(self._history)

    def send(self, message: str, **kwargs) -> ChatMessage:
        """
        Send a message to the crafts-ai server and return the reply.

        Args:
            message: User message text.
            **kwargs: Extra fields forwarded to the API payload.

        Returns:
            :class:`ChatMessage` with the assistant's reply.

        Raises:
            urllib.error.URLError: If the server is unreachable.
        """
        user_msg = ChatMessage(text=message, role="user", session_id=self.session_id)
        self._history.append(user_msg)

        payload = {
            "message": message,
            "session_id": self.session_id,
            **kwargs,
        }

        try:
            data = self.client.post("/chat", payload)
            reply_text = data.get("reply") or data.get("text") or data.get("message", "")
            reply = ChatMessage(
                text=reply_text,
                role="assistant",
                session_id=self.session_id,
                metadata=data,
            )
        except Exception as exc:
            logger.error("ChatBubble.send error: %s", exc)
            reply = ChatMessage(
                text=f"[Error: {exc}]",
                role="assistant",
                session_id=self.session_id,
            )

        self._history.append(reply)
        return reply

    def clear(self) -> None:
        """Clear the conversation history."""
        self._history.clear()

    def is_connected(self) -> bool:
        """Return True if the crafts-ai server is reachable."""
        return self.client.health()
