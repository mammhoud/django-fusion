"""
crafts_ai — Standalone AI/MCP toolkit. No Django required.

Package name matches the repo: crafts-ai
Import as `crafts_ai` or use the `nawa` namespace alias.

Sub-packages:
    ai          — OpenAI, Claude, Rasa, and generic AI integrations
    mcp         — Model Context Protocol server utilities
    seeder      — Faker-based data seeding (framework-agnostic)
    orchestrator — Spec task orchestration engine
    chat        — Chat bubble REST API client for crafts server

Usage::

    # Direct import
    from crafts_ai.ai.integrations import AIIntegrationRegistry

    # Via nawa namespace alias
    import crafts_ai as nawa
    ai = nawa.ai.integrations.AIIntegrationRegistry.get("openai")
"""
__version__ = "0.2.0"
__package_name__ = "crafts-ai"

# nawa namespace — import this package as `nawa` for short
from crafts_ai import ai, chat, mcp, orchestrator, seeder  # noqa: E402

__all__ = ["ai", "mcp", "seeder", "orchestrator", "chat", "__version__"]
