"""Static import inventory rules for the django-rseal to crafts-ai migration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImportRule:
    """Describe where a django-rseal import family should live."""

    prefix: str
    target: str
    status: str
    note: str


RSEAL_IMPORT_RULES: tuple[ImportRule, ...] = (
    ImportRule(
        prefix="django_rseal.ai",
        target="crafts_ai.ai",
        status="move-to-crafts-ai",
        note="AI provider adapters and prompt helpers should be framework agnostic.",
    ),
    ImportRule(
        prefix="django_rseal.mcp",
        target="crafts_ai.mcp_server",
        status="move-to-crafts-ai",
        note="MCP server integration belongs with the standalone AI toolkit.",
    ),
    ImportRule(
        prefix="django_rseal.workflows.orchestrator",
        target="crafts_ai.orchestrator",
        status="move-to-crafts-ai",
        note="Task orchestration can be represented without Django model imports.",
    ),
    ImportRule(
        prefix="django_rseal.blocks",
        target="django_rseal.blocks",
        status="keep-in-django-rseal",
        note="Wagtail blocks require Django/Wagtail and must not move into crafts_ai.",
    ),
    ImportRule(
        prefix="django_rseal.models",
        target="django_rseal.models",
        status="keep-in-django-rseal",
        note="Django models remain in the Django automation package.",
    ),
    ImportRule(
        prefix="django_rseal.pipelines.models",
        target="django_rseal.pipelines.models",
        status="keep-in-django-rseal",
        note="Pipeline models are Django-specific and should stay out of crafts_ai.",
    ),

    ImportRule(
        prefix="django_rseal.handlers.models",
        target="django_rseal.handlers.models",
        status="keep-in-django-rseal",
        note="Handler models depend on Django and project database integration.",
    ),
    ImportRule(
        prefix="django_rseal.contrib.core.models",
        target="django_rseal.contrib.core.models",
        status="keep-in-django-rseal",
        note="Contrib core models are Django ORM types used by website processors.",
    ),
    ImportRule(
        prefix="django_rseal.pipelines.services",
        target="django_rseal.pipelines.services",
        status="keep-in-django-rseal",
        note="Pipeline services coordinate website/domain runtime behavior.",
    ),
    ImportRule(
        prefix="django_rseal.middlewares",
        target="django_rseal.middlewares",
        status="keep-in-django-rseal",
        note="Middleware depends on Django request/response runtime.",
    ),
    ImportRule(
        prefix="django_rseal.services.infrastructure.jobs",
        target="django_rseal.services.infrastructure.jobs",
        status="keep-in-django-rseal",
        note="Job dispatch is tied to the website runtime and queue backend.",
    ),
)


def classify_import(import_path: str) -> ImportRule | None:
    """Return the first migration rule matching an import path."""
    for rule in RSEAL_IMPORT_RULES:
        if import_path == rule.prefix or import_path.startswith(f"{rule.prefix}."):
            return rule
    return None
