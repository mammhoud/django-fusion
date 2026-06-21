"""Static import inventory rules for the crafts-ai to crafts-ai migration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImportRule:
    """Describe where a crafts-ai import family should live."""

    prefix: str
    target: str
    status: str
    note: str


RSEAL_IMPORT_RULES: tuple[ImportRule, ...] = (
    ImportRule(
        prefix="crafts_ai.rseal.ai",
        target="crafts_ai.ai",
        status="move-to-crafts-ai",
        note="AI provider adapters and prompt helpers should be framework agnostic.",
    ),
    ImportRule(
        prefix="crafts_ai.rseal.mcp",
        target="crafts_ai.mcp_server",
        status="move-to-crafts-ai",
        note="MCP server integration belongs with the standalone AI toolkit.",
    ),
    ImportRule(
        prefix="crafts_ai.rseal.workflows.orchestrator",
        target="crafts_ai.orchestrator",
        status="move-to-crafts-ai",
        note="Task orchestration can be represented without Django model imports.",
    ),
    ImportRule(
        prefix="crafts_ai.rseal.blocks",
        target="crafts_ai.rseal.blocks",
        status="keep-in-crafts-ai",
        note="Wagtail blocks require Django/Wagtail and must not move into crafts_ai.",
    ),
    ImportRule(
        prefix="crafts_ai.rseal.models",
        target="crafts_ai.rseal.models",
        status="keep-in-crafts-ai",
        note="Django models remain in the Django automation package.",
    ),
    ImportRule(
        prefix="crafts_ai.rseal.pipelines.models",
        target="crafts_ai.rseal.pipelines.models",
        status="keep-in-crafts-ai",
        note="Pipeline models are Django-specific and should stay out of crafts_ai.",
    ),

    ImportRule(
        prefix="crafts_ai.rseal.handlers.models",
        target="crafts_ai.rseal.handlers.models",
        status="keep-in-crafts-ai",
        note="Handler models depend on Django and project database integration.",
    ),
    ImportRule(
        prefix="crafts_ai.rseal.contrib.core.models",
        target="crafts_ai.rseal.contrib.core.models",
        status="keep-in-crafts-ai",
        note="Contrib core models are Django ORM types used by website processors.",
    ),
    ImportRule(
        prefix="crafts_ai.rseal.pipelines.services",
        target="crafts_ai.rseal.pipelines.services",
        status="keep-in-crafts-ai",
        note="Pipeline services coordinate website/domain runtime behavior.",
    ),
    ImportRule(
        prefix="crafts_ai.rseal.middlewares",
        target="crafts_ai.rseal.middlewares",
        status="keep-in-crafts-ai",
        note="Middleware depends on Django request/response runtime.",
    ),
    ImportRule(
        prefix="crafts_ai.rseal.services.infrastructure.jobs",
        target="crafts_ai.rseal.services.infrastructure.jobs",
        status="keep-in-crafts-ai",
        note="Job dispatch is tied to the website runtime and queue backend.",
    ),
)


def classify_import(import_path: str) -> ImportRule | None:
    """Return the first migration rule matching an import path."""
    for rule in RSEAL_IMPORT_RULES:
        if import_path == rule.prefix or import_path.startswith(f"{rule.prefix}."):
            return rule
    return None
