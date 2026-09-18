"""In-project AI/MCP/chat services for TemplateTinker (replaces ceptor_stubs).

Provides:
    CeptorAIService    — AI completion/streaming via the in-project AIIntegrationRegistry
    CeptorMCPService   — MCP tool execution via the in-project MCP server
    CeptorConfigLoader — Configuration preloader
    CeptorChatService  — High-level chat interface with a local-AI fallback

Every provider call goes through the project's own real AI service
(``chat.services.AIService`` — Ollama + OpenAI-compatible), so no external
``ceptor-ai`` package or stub module is required.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Iterator

import httpx

from .constants import available_models, get_model
from .services import AIService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  Config Preloader
# ═══════════════════════════════════════════════════════════════

class CeptorConfigLoader:
    """Preload and cache AI configuration from YAML/JSON files.

    Usage::

        loader = CeptorConfigLoader(root=".")
        agent_configs = loader.load_agent_configs()
        theme_data = loader.load_theme_components()
    """

    def __init__(self, root: str | Path = "."):
        self.root = Path(root).resolve()
        self._cache: dict[str, Any] = {}

    def load_agent_configs(self) -> dict[str, Any]:
        """Load application/kilo/agent/*.json configs (cached)."""
        cache_key = "agent_configs"
        if cache_key in self._cache:
            return self._cache[cache_key]

        configs: dict[str, Any] = {}
        agent_dir = self.root / ".kilo" / "agent"
        if agent_dir.exists():
            for path in sorted(agent_dir.glob("*.json")):
                try:
                    configs[path.name] = json.loads(
                        path.read_text(encoding="utf-8")
                    )
                except (json.JSONDecodeError, OSError) as exc:
                    logger.warning("Failed to load %s: %s", path, exc)

        self._cache[cache_key] = configs
        return configs

    def load_models_config(self) -> dict[str, Any]:
        """Load models.yml from customizer configs directory."""
        cache_key = "models_config"
        if cache_key in self._cache:
            return self._cache[cache_key]

        import yaml

        models_path = (
            Path(__file__).resolve().parents[1] / "configs" / "models.yml"
        )
        if models_path.exists():
            with open(models_path, encoding="utf-8") as fh:
                config = yaml.safe_load(fh)
        else:
            config = {"models": []}

        self._cache[cache_key] = config
        return config

    def load_website_templates(self, website_slug: str) -> list[dict[str, Any]]:
        """Discover template files for a website from AI config."""
        from .site_data import pages_for_website

        data = pages_for_website(website_slug)
        return data["sections"] if data else []

    def get_model_by_id(self, model_id: str) -> dict[str, Any] | None:
        """Look up a model from the loaded config."""
        config = self.load_models_config()
        for model in config.get("models", []):
            if model.get("id") == model_id:
                return model
        return None

    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()


# ═══════════════════════════════════════════════════════════════
#  AI Integration Registry — real provider backends
# ═══════════════════════════════════════════════════════════════

# Backend name → model id resolved from configs/models.yml (or the virtual
# ceptor-* entries). These are the backends the UI exposes.
BACKEND_MODEL_MAP: dict[str, str] = {
    "ollama": "gemma3-4b",
    "openai": "gpt4o",
    "claude": "claude-sonnet",
    "gemini": "gemini-2.5-flash",
    "openai_compatible": "gpt4o",
}


def _resolve_model_id(backend: str, model: str | None) -> str:
    """Resolve a backend name + optional model hint to a real model id."""
    if model:
        if get_model(model) is not None or model in BACKEND_MODEL_MAP.values():
            return model
    return BACKEND_MODEL_MAP.get(backend, "gemma3-4b")


class _AIProviderBackend:
    """Real provider backend bound to a model id.

    Delegates to ``chat.services.AIService`` (Ollama + OpenAI-compatible),
    which is the project's production AI path.
    """

    def __init__(self, backend: str, model_id: str, **kwargs: Any):
        self.backend = backend
        self.model_id = model_id
        self.kwargs = kwargs

    def generate(self, prompt: str, **kwargs: Any) -> str:
        messages = [{"role": "user", "content": prompt}]
        return AIService.chat(self.model_id, messages)

    def stream(self, prompt: str, **kwargs: Any) -> Iterator[str]:
        messages = [{"role": "user", "content": prompt}]
        for raw in AIService.stream(self.model_id, messages):
            try:
                data = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue
            if data.get("type") == "token":
                yield data.get("content", "")


class AIIntegrationRegistry:
    """Registry for AI provider integrations.

    Replaces ``ceptor_ai.ai.integrations.AIIntegrationRegistry``. Backends are
    resolved to real model configs from ``configs/models.yml`` and executed
    through the in-project AI service — no stubs.
    """

    _backends: set[str] = set(BACKEND_MODEL_MAP.keys())

    @classmethod
    def register(cls, name: str) -> None:
        cls._backends.add(name)

    @classmethod
    def get(cls, backend: str, **inst_kwargs: Any) -> _AIProviderBackend:
        model_id = _resolve_model_id(backend, inst_kwargs.pop("model", None))
        return _AIProviderBackend(backend, model_id, **inst_kwargs)

    @classmethod
    def list_integrations(cls) -> list[str]:
        return sorted(cls._backends)


# ═══════════════════════════════════════════════════════════════
#  MCP Server — real read-only tool implementations
# ═══════════════════════════════════════════════════════════════

_SKIP_DIRS = {
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".astro",
    "dist",
    "build",
    "cache",
    "staticfiles",
}


_TOKEN_RE = re.compile(r"(--[a-zA-Z0-9_-]+)\s*:")


def _theme_analyzer(root: str) -> dict[str, Any]:
    """Scan a project root for CSS custom-property design tokens."""
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        return {"root": root, "error": "directory not found", "tokens": {}}

    tokens: dict[str, list[str]] = {}
    files_scanned = 0
    for path in root_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".css", ".scss"}:
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            files_scanned += 1
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for match in _TOKEN_RE.finditer(text):
                tokens.setdefault(match.group(1), []).append(str(path))

    return {
        "root": str(root_path),
        "files_scanned": files_scanned,
        "token_count": len(tokens),
        "tokens": {name: len(paths) for name, paths in sorted(tokens.items())},
    }


def _component_mapper(root: str, central: str) -> dict[str, Any]:
    """Find reusable component templates under a central directory."""
    root_path = Path(root).resolve()
    central_path = (root_path / central.lstrip("/")).resolve()

    if not central_path.is_dir():
        return {
            "root": str(root_path),
            "central": str(central_path),
            "error": "central directory not found",
            "components": [],
        }

    components: list[str] = []
    for path in central_path.rglob("*.html"):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if "components" in path.parts or "fragments" in path.parts:
            components.append(str(path.relative_to(root_path)))

    return {
        "root": str(root_path),
        "central": str(central_path),
        "component_count": len(components),
        "components": sorted(components),
    }


def _config_inspector(prefix: str | None) -> dict[str, Any]:
    """List env vars matching a prefix — names only, values redacted."""
    prefix = prefix or ""
    matched = [
        name
        for name in os.environ
        if name.startswith(prefix) and not name.startswith("_")
    ]
    return {
        "prefix": prefix,
        "count": len(matched),
        "variables": sorted(matched),
        "note": "Values are redacted; set the matching env vars to configure.",
    }


class _MCPServer:
    """Real in-project MCP tool server.

    Replaces ``ceptor_ai.mcp.server.server``. Tools are read-only and operate
    on the local filesystem / environment.
    """

    def list_tools(self) -> list[str]:
        return ["theme_analyzer", "component_mapper", "config_inspector"]

    def call_tool(self, tool_name: str, **kwargs: Any) -> Any:
        if tool_name == "theme_analyzer":
            return _theme_analyzer(kwargs.get("root", "."))
        if tool_name == "component_mapper":
            return _component_mapper(
                kwargs.get("root", "."),
                kwargs.get("central", "projects/precis-ctc"),
            )
        if tool_name == "config_inspector":
            return _config_inspector(kwargs.get("prefix"))
        raise ValueError(
            f"Unknown tool: {tool_name}. "
            f"Available: {', '.join(self.list_tools())}"
        )


server = _MCPServer()  # module-level instance


# ═══════════════════════════════════════════════════════════════
#  Chat client — real HTTP client with local-AI fallback
# ═══════════════════════════════════════════════════════════════

class _ChatReply:
    """A real chat reply returned by ChatBubble.send()."""

    def __init__(
        self, text: str, role: str = "assistant", session_id: str = ""
    ):
        self.text = text
        self.role = role
        self.session_id = session_id
        self.metadata: dict[str, Any] = {"source": "chat-server"}


class CraftsClient:
    """Real chat server client — replaces ceptor_ai.chat.client.CraftsClient."""

    def __init__(self, base_url: str = "http://localhost:8765", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> bool:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/health")
                return response.status_code < 400
        except Exception:
            return False


class ChatBubble:
    """Real chat bubble — replaces ceptor_ai.chat.client.ChatBubble.

    Sends messages to the configured chat server. When the server is
    unreachable it falls back to the local AI service (Ollama by default) so a
    real reply is always produced.
    """

    def __init__(
        self,
        server_url: str = "http://localhost:8765",
        session_id: str | None = None,
        timeout: int = 30,
    ):
        self.server_url = server_url.rstrip("/")
        self.session_id = session_id
        self.timeout = timeout

    def send(self, message: str, **kwargs: Any) -> _ChatReply:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.server_url}/chat",
                    json={
                        "message": message,
                        "session_id": self.session_id,
                        **kwargs,
                    },
                )
                response.raise_for_status()
                data = response.json()
            text = (
                data.get("text")
                or data.get("reply")
                or data.get("message", {}).get("content", "")
            )
            return _ChatReply(
                text=str(text),
                role=data.get("role", "assistant"),
                session_id=data.get("session_id", self.session_id or ""),
            )
        except Exception as exc:
            # Chat server unavailable — fall back to the local AI service.
            logger.warning(
                "Chat server unreachable (%s); falling back to local AI: %s",
                self.server_url,
                exc,
            )
            try:
                reply = AIService.chat(
                    _resolve_model_id("ollama", None),
                    [{"role": "user", "content": message}],
                )
            except Exception as fallback_exc:
                raise RuntimeError(
                    f"Chat server unreachable and local AI failed: {fallback_exc}"
                ) from fallback_exc
            return _ChatReply(
                text=str(reply),
                role="assistant",
                session_id=self.session_id or "",
            )


# ═══════════════════════════════════════════════════════════════
#  AI Service — real completions via the in-project registry
# ═══════════════════════════════════════════════════════════════

class CeptorAIService:
    """AI completions via the in-project AIIntegrationRegistry.

    Usage::

        svc = CeptorAIService()
        reply = svc.generate("openai", "Explain Django class-based views")
        for chunk in svc.stream("claude", "Summarize this code"):
            print(chunk, end="")
    """

    def generate(
        self,
        backend: str,
        prompt: str,
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a non-streaming completion."""
        inst = AIIntegrationRegistry.get(backend, model=model, **kwargs)
        return inst.generate(prompt, **kwargs)

    def stream(
        self,
        backend: str,
        prompt: str,
        model: str | None = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Stream completion tokens."""
        inst = AIIntegrationRegistry.get(backend, model=model, **kwargs)
        return inst.stream(prompt, **kwargs)

    def list_backends(self) -> list[str]:
        """Return available AI integration backends."""
        return AIIntegrationRegistry.list_integrations()


# ═══════════════════════════════════════════════════════════════
#  MCP Service — real tool execution
# ═══════════════════════════════════════════════════════════════

class CeptorMCPService:
    """MCP tool execution via the in-project MCP server.

    Usage::

        mcp = CeptorMCPService(root=".")
        result = mcp.run_tool("theme_analyzer", root="/path/to/project")
        config = mcp.run_tool("config_inspector", prefix="DJANGO")
    """

    def __init__(self, name: str = "ceptorai-mcp", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._server = server

    def _get_server(self) -> _MCPServer:
        return self._server

    def run_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a named MCP tool."""
        srv = self._get_server()

        if tool_name not in srv.list_tools():
            available = srv.list_tools()
            raise ValueError(
                f"Unknown tool: {tool_name}. "
                f"Available: {', '.join(available)}"
            )

        return srv.call_tool(tool_name, **kwargs)

    def list_tools(self) -> list[str]:
        """List available MCP tools."""
        return self._get_server().list_tools()

    def analyze_themes(self, root: str = ".") -> dict[str, Any]:
        """Run theme_analyzer on a project root."""
        return self.run_tool("theme_analyzer", root=root)

    def map_components(self, root: str = ".", central: str = "projects/precis-ctc") -> dict[str, Any]:
        """Run component_mapper to find reusable components."""
        return self.run_tool("component_mapper", root=root, central=central)

    def inspect_config(self, prefix: str | None = None) -> dict[str, Any]:
        """Run config_inspector with optional env var prefix filter."""
        return self.run_tool("config_inspector", prefix=prefix)


# ═══════════════════════════════════════════════════════════════
#  Chat Service — real chat with local-AI fallback
# ═══════════════════════════════════════════════════════════════

class CeptorChatService:
    """High-level chat interface using the real ChatBubble.

    Usage::

        chat = CeptorChatService(server_url="http://localhost:8765")
        reply = chat.send("Hello!")
        print(reply["text"])
    """

    def __init__(
        self,
        server_url: str = "http://localhost:8765",
        timeout: int = 30,
    ):
        self.server_url = server_url
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if the chat server (or the local AI fallback) is reachable."""
        client = CraftsClient(base_url=self.server_url, timeout=self.timeout)
        if client.health():
            return True
        # The local AI fallback means a reply is still producible.
        try:
            AIService._resolve_model(_resolve_model_id("ollama", None))
            return True
        except Exception:
            return False

    def send_message(
        self, message: str, session_id: str | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Send a message and return the reply as a dict."""
        try:
            bubble = ChatBubble(
                server_url=self.server_url,
                session_id=session_id,
                timeout=self.timeout,
            )
            reply = bubble.send(message, **kwargs)
            return {
                "text": reply.text,
                "role": reply.role,
                "session_id": reply.session_id,
                "metadata": reply.metadata,
            }
        except Exception as exc:
            logger.error("CeptorChatService.send error: %s", exc)
            return {
                "text": f"[Error: {exc}]",
                "role": "assistant",
                "session_id": session_id or "",
                "metadata": {"error": str(exc)},
            }


# ═══════════════════════════════════════════════════════════════
#  Singleton helpers
# ═══════════════════════════════════════════════════════════════

_config_loader: CeptorConfigLoader | None = None
_ai_service: CeptorAIService | None = None
_mcp_service: CeptorMCPService | None = None


def get_config_loader(root: str | Path = ".") -> CeptorConfigLoader:
    """Return the singleton CeptorConfigLoader."""
    global _config_loader
    if _config_loader is None:
        _config_loader = CeptorConfigLoader(root=root)
    return _config_loader


def get_ai_service() -> CeptorAIService:
    """Return the singleton CeptorAIService."""
    global _ai_service
    if _ai_service is None:
        _ai_service = CeptorAIService()
    return _ai_service


def get_mcp_service() -> CeptorMCPService:
    """Return the singleton CeptorMCPService."""
    global _mcp_service
    if _mcp_service is None:
        _mcp_service = CeptorMCPService()
    return _mcp_service
