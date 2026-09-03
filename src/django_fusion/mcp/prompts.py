"""Read-only prompt catalog access for django-fusion MCP servers.

This is a generalized version of the Kilo prompt catalog (.agents/mcp/).
Projects can mount their own catalog by setting ``FUSION_MCP_PROMPT_CATALOG_PATH``
in Django settings or by passing an explicit ``catalog_path``.

No prompt is executed, interpolated, or allowed to perform repository actions.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# From libs/django-fusion/src/django_fusion/mcp/prompts.py, parents[5]
# reaches the monorepo root (structa.cloud/). The Kilo prompt catalog now
# lives under .agents/mcp/prompts/ (formerly applications/agents/prompts/).
_DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[5] / ".agents" / "mcp" / "prompts" / "catalog.json"


class PromptCatalogError(RuntimeError):
    """Raised when the prompt catalog cannot be read or validated."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_catalog_path() -> Path:
    """Resolve the catalog JSON path from Django settings or fall back to default."""
    try:
        from django.conf import settings

        configured = getattr(settings, "FUSION_MCP_PROMPT_CATALOG_PATH", None)
        if configured:
            path = Path(configured)
            if path.is_file():
                return path
            logger.warning(
                "FUSION_MCP_PROMPT_CATALOG_PATH is set but not a file: %s", configured
            )
    except Exception:
        pass
    return _DEFAULT_CATALOG_PATH


def _get_agents_dir(catalog_path: Path) -> Path:
    """Return the agent definitions directory alongside the catalog."""
    return catalog_path.parent.parent / "agent"


def _get_skills_roots(catalog_path: Path) -> list[Path]:
    """Return skill directories to scan."""
    agents_dir = catalog_path.parent.parent
    repo_root = catalog_path.parents[3]
    return [
        agents_dir / "skills",
        repo_root / ".agents" / "skills",
    ]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _registered_agent_ids(agents_dir: Path) -> set[str]:
    ids: set[str] = set()
    if not agents_dir.is_dir():
        return ids
    for path in agents_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data.get("name"), str):
            ids.add(data["name"])
    return ids


def _registered_skill_ids(skills_roots: Sequence[Path]) -> set[str]:
    ids: set[str] = set()
    for root in skills_roots:
        if not root.exists():
            continue
        for path in root.glob("*/SKILL.md"):
            first = path.read_text(encoding="utf-8", errors="replace")[:800]
            for line in first.splitlines():
                if line.startswith("name:"):
                    ids.add(line.split(":", 1)[1].strip())
                    break
            else:
                ids.add(path.parent.name)
    return ids


def _require_text(item: dict[str, Any], fields: tuple[str, ...], kind: str) -> None:
    for field in fields:
        if not isinstance(item.get(field), str) or not item[field].strip():
            raise PromptCatalogError(f"{kind} {item.get('id')} is missing: {field}")


def _require_list(item: dict[str, Any], fields: tuple[str, ...], kind: str) -> None:
    for field in fields:
        if not isinstance(item.get(field), list) or not item[field]:
            raise PromptCatalogError(f"{kind} {item.get('id')} needs: {field}")
        if not all(isinstance(v, str) and v.strip() for v in item[field]):
            raise PromptCatalogError(f"{kind} {item.get('id')} needs non-empty strings in {field}")


def _validate_skill(prompt: dict[str, Any], agent_ids: set[str], skill_ids: set[str]) -> None:
    _require_text(prompt, ("id", "title", "description", "agent", "prompt", "safety"), kind="Skill")
    _require_list(prompt, ("expected_output", "inputs"), kind="Skill")
    if prompt["agent"] not in agent_ids:
        raise PromptCatalogError(f"Skill {prompt['id']} refs unknown agent: {prompt['agent']}")
    for agent in prompt.get("supporting_agents", []):
        if not isinstance(agent, str) or agent not in agent_ids:
            raise PromptCatalogError(f"Skill {prompt['id']} refs unknown supporting agent: {agent}")
    for skill in prompt.get("skills", []):
        if not isinstance(skill, str) or skill not in skill_ids:
            raise PromptCatalogError(f"Skill {prompt['id']} refs unknown skill: {skill}")


def _validate_project(
    prompt: dict[str, Any], agent_ids: set[str], skill_ids: set[str], catalog_skill_ids: set[str]
) -> None:
    _require_text(prompt, ("id", "name", "path", "description", "prompt"), kind="Project")
    _require_list(prompt, ("stack", "agent_sequence", "checks", "related_skills"), kind="Project")
    for agent in prompt["agent_sequence"]:
        if agent not in agent_ids:
            raise PromptCatalogError(f"Project {prompt['id']} refs unknown agent: {agent}")
    for skill in prompt["related_skills"]:
        if skill not in catalog_skill_ids and skill not in skill_ids:
            raise PromptCatalogError(f"Project {prompt['id']} refs unknown skill: {skill}")


def _validate_workflow(prompt: dict[str, Any], agent_ids: set[str]) -> None:
    _require_text(prompt, ("id", "title", "description"), kind="Workflow")
    _require_list(prompt, ("agents", "steps"), kind="Workflow")
    for agent in prompt["agents"]:
        if agent not in agent_ids:
            raise PromptCatalogError(f"Workflow {prompt['id']} refs unknown agent: {agent}")


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def load_prompt_catalog(catalog_path: Path | None = None) -> dict[str, Any]:
    """Load and validate the static catalog. Cached per process."""
    path = catalog_path or _resolve_catalog_path()
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PromptCatalogError(f"Unable to load prompt catalog: {exc}") from exc
    if not isinstance(catalog, dict):
        raise PromptCatalogError("Root must be an object")
    if catalog.get("schema_version") != "1.0":
        raise PromptCatalogError("Unsupported schema_version")

    agents_dir = _get_agents_dir(path)
    skills_roots = _get_skills_roots(path)
    agent_ids = _registered_agent_ids(agents_dir)
    skill_ids = _registered_skill_ids(skills_roots)
    catalog_skill_ids = {
        item["id"]
        for item in catalog.get("skill_prompts", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    seen: set[str] = set()
    for name in ("skill_prompts", "projects", "workflows"):
        collection = catalog.get(name)
        if not isinstance(collection, list) or not collection:
            raise PromptCatalogError(f"Non-empty {name} list required")
        for item in collection:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise PromptCatalogError(f"Invalid item in {name}")
            if item["id"] in seen:
                raise PromptCatalogError(f"Duplicate id: {item['id']}")
            seen.add(item["id"])
            if name == "skill_prompts":
                _validate_skill(item, agent_ids=agent_ids, skill_ids=skill_ids)
            elif name == "projects":
                _validate_project(
                    item, agent_ids=agent_ids, skill_ids=skill_ids, catalog_skill_ids=catalog_skill_ids
                )
            else:
                _validate_workflow(item, agent_ids=agent_ids)
    return catalog


def _all_items() -> list[dict[str, Any]]:
    catalog = load_prompt_catalog()
    return [*catalog["skill_prompts"], *catalog["projects"], *catalog["workflows"]]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def list_prompt_metadata() -> dict[str, Any]:
    """Return concise metadata suitable for an MCP prompt catalog listing."""
    items = _all_items()
    return {
        "schema_version": load_prompt_catalog()["schema_version"],
        "count": len(items),
        "prompts": [
            {
                "id": item["id"],
                "title": item.get("title", item.get("name")),
                "description": item["description"],
                "kind": (
                    "skill"
                    if item["id"].startswith("skill.")
                    else "project" if item["id"].startswith("project.") else "workflow"
                ),
                "agent": item.get("agent"),
                "agents": item.get("agent_sequence", item.get("agents")),
                "projects": item.get("projects"),
            }
            for item in items
        ],
    }


def get_prompt(prompt_id: str) -> dict[str, Any] | None:
    """Return one complete prompt definition by stable ID."""
    if not isinstance(prompt_id, str) or not prompt_id.strip():
        return None
    return next((item for item in _all_items() if item["id"] == prompt_id), None)
