"""
ceptor_ai integration for TemplateTinker — wraps ceptor-ai features as APIs.

Provides:
    CeptorAPIClient   — HTTP client for the ceptor-ai REST API
    CeptorAIService   — AI completion/streaming via ceptor_ai.ai.integrations
    CeptorMCPService  — MCP tool execution via ceptor_ai.mcp.server
    CeptorConfigLoader — Configuration preloader for ceptor-ai configs
    CeptorChatService — High-level chat interface using ceptor_ai.chat
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  Config Preloader
# ═══════════════════════════════════════════════════════════════

class CeptorConfigLoader:
    """Preload and cache ceptor-ai configuration from YAML/JSON files.

    Usage::

        loader = CeptorConfigLoader(root=".")
        agent_configs = loader.load_agent_configs()
        theme_data = loader.load_theme_components()
    """

    def __init__(self, root: str | Path = "."):
        self.root = Path(root).resolve()
        self._cache: dict[str, Any] = {}

    def load_agent_configs(self) -> dict[str, Any]:
        """Load applications/kilo/agent/*.json configs (cached)."""
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
        """Discover template files for a website from ceptor-ai config."""
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
#  AI Service — using ceptor_ai.ai.integrations
# ═══════════════════════════════════════════════════════════════

class CeptorAIService:
    """AI completions via ceptor_ai.ai.integrations (OpenAI, Claude, etc.).

    Automatically resolves API keys from environment variables.

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
        try:
            from ceptor_ai.ai.integrations import AIIntegrationRegistry
        except ImportError:
            raise ImportError(
                "ceptor-ai is not installed. "
                "Install it with: pip install ceptor-ai"
            )

        inst_kwargs = {**kwargs}
        if model:
            inst_kwargs["model"] = model
        inst = AIIntegrationRegistry.get(backend, **inst_kwargs)
        return inst.generate(prompt, **kwargs)

    def stream(
        self,
        backend: str,
        prompt: str,
        model: str | None = None,
        **kwargs: Any,
    ):
        """Stream completion tokens."""
        try:
            from ceptor_ai.ai.integrations import AIIntegrationRegistry
        except ImportError:
            raise ImportError(
                "ceptor-ai is not installed. "
                "Install it with: pip install ceptor-ai"
            )

        inst_kwargs = {**kwargs}
        if model:
            inst_kwargs["model"] = model
        inst = AIIntegrationRegistry.get(backend, **inst_kwargs)
        return inst.stream(prompt, **kwargs)

    def list_backends(self) -> list[str]:
        """Return available AI integration backends."""
        try:
            from ceptor_ai.ai.integrations import AIIntegrationRegistry

            return AIIntegrationRegistry.list_integrations()
        except ImportError:
            return []


# ═══════════════════════════════════════════════════════════════
#  MCP Service — using ceptor_ai.mcp.server
# ═══════════════════════════════════════════════════════════════

class CeptorMCPService:
    """MCP tool execution via ceptor_ai.mcp.server.

    Usage::

        mcp = CeptorMCPService(root=".")
        result = mcp.run_tool("theme_analyzer", root="/path/to/project")
        config = mcp.run_tool("config_inspector", prefix="DJANGO")
    """

    def __init__(self, name: str = "ceptorai-mcp", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._server = None

    def _get_server(self):
        """Lazy-load the MCP server."""
        if self._server is not None:
            return self._server

        try:
            from ceptor_ai.mcp.server import server as mcp_server_instance

            self._server = mcp_server_instance
            return self._server
        except ImportError:
            raise ImportError(
                "ceptor-ai MCP is not available. "
                "Install ceptor-ai[mcp] for MCP support."
            )

    def run_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a named MCP tool."""
        server = self._get_server()

        if tool_name not in server.list_tools():
            available = server.list_tools()
            raise ValueError(
                f"Unknown tool: {tool_name}. "
                f"Available: {', '.join(available)}"
            )

        return server.call_tool(tool_name, **kwargs)

    def list_tools(self) -> list[str]:
        """List available MCP tools."""
        return self._get_server().list_tools()

    def analyze_themes(self, root: str = ".") -> dict[str, Any]:
        """Run theme_analyzer on a project root."""
        return self.run_tool("theme_analyzer", root=root)

    def map_components(self, root: str = ".", central: str = "core/ctc-research") -> dict[str, Any]:
        """Run component_mapper to find reusable components."""
        return self.run_tool("component_mapper", root=root, central=central)

    def inspect_config(self, prefix: str | None = None) -> dict[str, str]:
        """Run config_inspector with optional env var prefix filter."""
        return self.run_tool("config_inspector", prefix=prefix)


# ═══════════════════════════════════════════════════════════════
#  Chat Service — using ceptor_ai.chat
# ═══════════════════════════════════════════════════════════════

class CeptorChatService:
    """High-level chat interface using ceptor_ai.chat.ChatBubble.

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
        """Check if the ceptor-ai chat server is reachable."""
        try:
            from ceptor_ai.chat.client import CraftsClient

            client = CraftsClient(
                base_url=self.server_url, timeout=self.timeout
            )
            return client.health()
        except ImportError:
            return False
        except Exception:
            return False

    def send_message(
        self, message: str, session_id: str | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Send a message and return the reply as a dict."""
        try:
            from ceptor_ai.chat.client import ChatBubble

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
        except ImportError:
            raise ImportError(
                "ceptor-ai is not installed. "
                "Install it with: pip install ceptor-ai"
            )
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
