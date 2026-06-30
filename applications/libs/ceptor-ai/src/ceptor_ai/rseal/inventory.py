"""Static import inventory rules for the ceptor-ai to ceptor-ai migration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImportRule:
    """Describe where a ceptor-ai import family should live."""

    prefix: str
    target: str
    status: str
    note: str


RSEAL_IMPORT_RULES: tuple[ImportRule, ...] = (
    ImportRule(
        prefix="ceptor_ai.ai",
        target="ceptor_ai.ai",
        status="move-to-ceptor-ai",
        note="AI provider adapters and prompt helpers should be framework agnostic.",
    ),
    ImportRule(
        prefix="ceptor_ai.mcp",
        target="ceptor_ai.mcp_server",
        status="move-to-ceptor-ai",
        note="MCP server integration belongs with the standalone AI toolkit.",
    ),
    ImportRule(
        prefix="ceptor_ai.workflows.orchestrator",
        target="ceptor_ai.orchestrator",
        status="move-to-ceptor-ai",
        note="Task orchestration can be represented without Django model imports.",
    ),
    ImportRule(
        prefix="ceptor_ai.blocks",
        target="ceptor_ai.blocks",
        status="keep-in-ceptor-ai",
        note="Wagtail blocks require Django/Wagtail and must not move into ceptor_ai.",
    ),
    ImportRule(
        prefix="ceptor_ai.models",
        target="ceptor_ai.models",
        status="keep-in-ceptor-ai",
        note="Django models remain in the Django automation package.",
    ),
    ImportRule(
        prefix="ceptor_ai.pipelines.models",
        target="ceptor_ai.pipelines.models",
        status="keep-in-ceptor-ai",
        note="Pipeline models are Django-specific and should stay out of ceptor_ai.",
    ),

    ImportRule(
        prefix="ceptor_ai.handlers.models",
        target="ceptor_ai.handlers.models",
        status="keep-in-ceptor-ai",
        note="Handler models depend on Django and project database integration.",
    ),
    ImportRule(
        prefix="ceptor_ai.contrib.core.models",
        target="ceptor_ai.contrib.core.models",
        status="keep-in-ceptor-ai",
        note="Contrib core models are Django ORM types used by website processors.",
    ),
    ImportRule(
        prefix="ceptor_ai.pipelines.services",
        target="ceptor_ai.pipelines.services",
        status="keep-in-ceptor-ai",
        note="Pipeline services coordinate website/domain runtime behavior.",
    ),
    ImportRule(
        prefix="ceptor_ai.middlewares",
        target="ceptor_ai.middlewares",
        status="keep-in-ceptor-ai",
        note="Middleware depends on Django request/response runtime.",
    ),
    ImportRule(
        prefix="ceptor_ai.services.infrastructure.jobs",
        target="ceptor_ai.services.infrastructure.jobs",
        status="keep-in-ceptor-ai",
        note="Job dispatch is tied to the website runtime and queue backend.",
    ),
)


def classify_import(import_path: str) -> ImportRule | None:
    """Return the first migration rule matching an import path."""
    for rule in RSEAL_IMPORT_RULES:
        if import_path == rule.prefix or import_path.startswith(f"{rule.prefix}."):
            return rule
    return None
