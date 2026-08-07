"""Local stubs for ceptor-ai AI/MCP/chat modules — inlined into cypercloud.

Replaces:
  - ceptor_ai.ai.integrations.AIIntegrationRegistry
  - ceptor_ai.mcp.server.server
  - ceptor_ai.chat.client.CraftsClient
  - ceptor_ai.chat.client.ChatBubble
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  AIIntegrationRegistry — AI provider registry
# ═══════════════════════════════════════════════════════════════

class _StubAIBackend:
    """Stub backend returned by AIIntegrationRegistry.get()."""

    def __init__(self, backend: str, **kwargs: Any):
        self.backend = backend
        self.kwargs = kwargs

    def generate(self, prompt: str, **kwargs: Any) -> str:
        logger.warning(
            "AIIntegrationRegistry.generate stub called for backend=%r",
            self.backend,
        )
        return f"[Stub AI ({self.backend})] No real AI backend configured."

    def stream(self, prompt: str, **kwargs: Any):
        logger.warning(
            "AIIntegrationRegistry.stream stub called for backend=%r",
            self.backend,
        )
        yield f"[Stub AI ({self.backend})] No real AI backend configured."


class AIIntegrationRegistry:
    """Registry for AI provider integrations.

    Replaces ceptor_ai.ai.integrations.AIIntegrationRegistry.
    When no real backends are configured, returns stubs.
    """

    _backends: dict[str, type] = {}

    @classmethod
    def register(cls, name: str, backend_cls: type) -> None:
        cls._backends[name] = backend_cls

    @classmethod
    def get(cls, backend: str, **inst_kwargs: Any) -> Any:
        backend_cls = cls._backends.get(backend)
        if backend_cls is not None:
            return backend_cls(**inst_kwargs)
        logger.warning("No AI backend registered for %r, using stub", backend)
        return _StubAIBackend(backend, **inst_kwargs)

    @classmethod
    def list_integrations(cls) -> list[str]:
        return list(cls._backends.keys())


# ═══════════════════════════════════════════════════════════════
#  MCP Server stub
# ═══════════════════════════════════════════════════════════════

class _StubMCPServer:
    """Stub MCP server — replaces ceptor_ai.mcp.server.server."""

    def list_tools(self) -> list[str]:
        return []

    def call_tool(self, tool_name: str, **kwargs: Any) -> Any:
        logger.warning("MCP stub: call_tool(%r, %s)", tool_name, kwargs)
        return {"status": "stub", "tool": tool_name, "args": kwargs}


server = _StubMCPServer()  # module-level instance


# ═══════════════════════════════════════════════════════════════
#  Chat client stubs
# ═══════════════════════════════════════════════════════════════

class _StubChatReply:
    """Stub chat reply returned by ChatBubble.send()."""

    def __init__(self, text: str = "", role: str = "assistant", session_id: str = ""):
        self.text = text
        self.role = role
        self.session_id = session_id
        self.metadata: dict[str, Any] = {"stub": True}


class CraftsClient:
    """Stub chat server client — replaces ceptor_ai.chat.client.CraftsClient."""

    def __init__(self, base_url: str = "http://localhost:8765", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout

    def health(self) -> bool:
        logger.debug("CraftsClient.health() stub — returning False")
        return False


class ChatBubble:
    """Stub chat bubble — replaces ceptor_ai.chat.client.ChatBubble."""

    def __init__(
        self,
        server_url: str = "http://localhost:8765",
        session_id: str | None = None,
        timeout: int = 30,
    ):
        self.server_url = server_url
        self.session_id = session_id
        self.timeout = timeout

    def send(self, message: str, **kwargs: Any) -> _StubChatReply:
        logger.warning(
            "ChatBubble.send() stub — chat server not available. "
            "Message: %.80s",
            message,
        )
        return _StubChatReply(
            text="[Chat stub] No chat server configured.",
            role="assistant",
            session_id=self.session_id or "",
        )


# ═══════════════════════════════════════════════════════════════
#  Default stub backends — register standard provider names so
#  ``list_integrations()`` reports them and API endpoints can route
#  through the inline stubs instead of rejecting every backend.
# ═══════════════════════════════════════════════════════════════

def _make_stub_backend(name: str) -> type[_StubAIBackend]:
    """Return a _StubAIBackend subclass that bakes in its backend name.

    ``AIIntegrationRegistry.get()`` instantiates registered backends with
    only ``**inst_kwargs`` (no ``backend`` positional), so each default
    backend needs its name bound at class creation time.
    """

    class _NamedStubBackend(_StubAIBackend):
        def __init__(self, **kwargs: Any):
            super().__init__(name, **kwargs)

    _NamedStubBackend.__name__ = f"_Stub{name.title()}Backend"
    return _NamedStubBackend


for _stub_backend_name in ("openai", "claude", "gemini"):
    AIIntegrationRegistry.register(
        _stub_backend_name, _make_stub_backend(_stub_backend_name)
    )
