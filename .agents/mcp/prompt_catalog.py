"""Read-only access to the repository's agent prompt catalog.

Delegates to ``django_fusion.mcp.prompts`` when django-fusion is available;
falls back to the local implementation when used standalone (e.g., in tests).
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Delegate to django-fusion when available
try:
    from django_fusion.mcp.prompts import get_prompt as _fusion_get_prompt
    from django_fusion.mcp.prompts import list_prompt_metadata as _fusion_list_prompt_metadata

    _DELEGATE_TO_FUSION = True
except ImportError:
    _DELEGATE_TO_FUSION = False
    logger.debug("django_fusion.mcp.prompts not available, using local catalog")

_CATALOG_PATH = Path(__file__).resolve().parent / "prompts" / "catalog.json"


class PromptCatalogError(RuntimeError):
    """Raised when the prompt catalog cannot be read or validated."""


def _registered_agent_ids() -> set[str]:
    """Read role IDs from the existing agent definitions without importing them."""
    ids: set[str] = set()
    for path in (_CATALOG_PATH.parent.parent / "agent").glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data.get("name"), str):
            ids.add(data["name"])
    return ids


def _registered_skill_ids() -> set[str]:
    """Read skill IDs from scoped skill frontmatter and the shared skill tree."""
    ids: set[str] = set()
    roots = [
        _CATALOG_PATH.parent.parent / "skills",
        _CATALOG_PATH.parents[3] / ".agents" / "skills",
    ]
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("*/SKILL.md"):
            first_lines = path.read_text(encoding="utf-8", errors="replace")[:800]
            for line in first_lines.splitlines():
                if line.startswith("name:"):
                    ids.add(line.split(":", 1)[1].strip())
                    break
            else:
                ids.add(path.parent.name)
    return ids


def _require_text(item: dict[str, Any], fields: tuple[str, ...], *, kind: str) -> None:
    missing = [field for field in fields if not isinstance(item.get(field), str) or not item[field].strip()]
    if missing:
        raise PromptCatalogError(f"{kind} {item.get('id')} is missing: {', '.join(missing)}")


def _require_list(item: dict[str, Any], fields: tuple[str, ...], *, kind: str) -> None:
    missing = [field for field in fields if not isinstance(item.get(field), list) or not item[field]]
    if missing:
        raise PromptCatalogError(f"{kind} {item.get('id')} needs: {', '.join(missing)}")
    for field in fields:
        if not all(isinstance(value, str) and value.strip() for value in item[field]):
            raise PromptCatalogError(f"{kind} {item.get('id')} needs non-empty strings in {field}")


def _validate_skill_prompt(prompt: dict[str, Any], *, agent_ids: set[str], skill_ids: set[str]) -> None:
    _require_text(prompt, ("id", "title", "description", "agent", "prompt", "safety"), kind="Skill prompt")
    _require_list(prompt, ("expected_output", "inputs"), kind="Skill prompt")
    if prompt["agent"] not in agent_ids:
        raise PromptCatalogError(f"Skill prompt {prompt['id']} references unknown agent: {prompt['agent']}")
    if not isinstance(prompt.get("supporting_agents", []), list):
        raise PromptCatalogError(f"Skill prompt {prompt['id']} needs supporting_agents as a list")
    if not all(isinstance(agent, str) and agent.strip() for agent in prompt.get("supporting_agents", [])):
        raise PromptCatalogError(f"Skill prompt {prompt['id']} needs non-empty supporting agent IDs")
    for agent in prompt.get("supporting_agents", []):
        if agent not in agent_ids:
            raise PromptCatalogError(f"Skill prompt {prompt['id']} references unknown supporting agent: {agent}")
    if not isinstance(prompt.get("skills", []), list):
        raise PromptCatalogError(f"Skill prompt {prompt['id']} needs skills as a list")
    if not all(isinstance(skill, str) and skill.strip() for skill in prompt.get("skills", [])):
        raise PromptCatalogError(f"Skill prompt {prompt['id']} needs non-empty skill IDs")
    for skill in prompt.get("skills", []):
        if skill not in skill_ids:
            raise PromptCatalogError(f"Skill prompt {prompt['id']} references unknown skill: {skill}")


def _validate_project_prompt(
    prompt: dict[str, Any],
    *,
    agent_ids: set[str],
    skill_ids: set[str],
    catalog_skill_ids: set[str],
) -> None:
    _require_text(prompt, ("id", "name", "path", "description", "prompt"), kind="Project prompt")
    _require_list(prompt, ("stack", "agent_sequence", "checks", "related_skills"), kind="Project prompt")
    for agent in prompt["agent_sequence"]:
        if agent not in agent_ids:
            raise PromptCatalogError(f"Project prompt {prompt['id']} references unknown agent: {agent}")
    for skill in prompt["related_skills"]:
        if skill not in catalog_skill_ids and skill not in skill_ids:
            raise PromptCatalogError(f"Project prompt {prompt['id']} references unknown catalog skill: {skill}")


def _validate_workflow(prompt: dict[str, Any], *, agent_ids: set[str]) -> None:
    _require_text(prompt, ("id", "title", "description"), kind="Workflow")
    _require_list(prompt, ("agents", "steps"), kind="Workflow")
    for agent in prompt["agents"]:
        if agent not in agent_ids:
            raise PromptCatalogError(f"Workflow {prompt['id']} references unknown agent: {agent}")


@lru_cache(maxsize=1)
def load_prompt_catalog() -> dict[str, Any]:
    """Load and validate the static catalog once per process."""
    try:
        catalog = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PromptCatalogError(f"Unable to load prompt catalog: {exc}") from exc
    if not isinstance(catalog, dict):
        raise PromptCatalogError("Prompt catalog root must be an object")
    if catalog.get("schema_version") != "1.0":
        raise PromptCatalogError("Unsupported prompt catalog schema_version")

    agent_ids = _registered_agent_ids()
    skill_ids = _registered_skill_ids()
    catalog_skill_ids = {
        item["id"]
        for item in catalog.get("skill_prompts", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    seen: set[str] = set()
    for collection_name in ("skill_prompts", "projects", "workflows"):
        collection = catalog.get(collection_name)
        if not isinstance(collection, list) or not collection:
            raise PromptCatalogError(f"Prompt catalog needs a non-empty {collection_name} list")
        for item in collection:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise PromptCatalogError(f"Invalid item in {collection_name}")
            if item["id"] in seen:
                raise PromptCatalogError(f"Duplicate prompt id: {item['id']}")
            seen.add(item["id"])
            if collection_name == "skill_prompts":
                _validate_skill_prompt(item, agent_ids=agent_ids, skill_ids=skill_ids)
            elif collection_name == "projects":
                _validate_project_prompt(
                    item,
                    agent_ids=agent_ids,
                    skill_ids=skill_ids,
                    catalog_skill_ids=catalog_skill_ids,
                )
            else:
                _validate_workflow(item, agent_ids=agent_ids)
    return catalog


def _prompt_items() -> list[dict[str, Any]]:
    catalog = load_prompt_catalog()
    return [*catalog["skill_prompts"], *catalog["projects"], *catalog["workflows"]]


def list_prompt_metadata() -> dict[str, Any]:
    """Return concise metadata suitable for an MCP prompt catalog listing."""
    if _DELEGATE_TO_FUSION:
        return _fusion_list_prompt_metadata()
    items = _prompt_items()
    return {
        "schema_version": load_prompt_catalog()["schema_version"],
        "count": len(items),
        "prompts": [
            {
                "id": item["id"],
                "title": item.get("title", item.get("name")),
                "description": item["description"],
                "kind": "skill" if item["id"].startswith("skill.") else "project" if item["id"].startswith("project.") else "workflow",
                "agent": item.get("agent"),
                "agents": item.get("agent_sequence", item.get("agents")),
                "projects": item.get("projects"),
            }
            for item in items
        ],
    }


def get_prompt(prompt_id: str) -> dict[str, Any] | None:
    """Return one complete prompt definition by stable ID."""
    if _DELEGATE_TO_FUSION:
        return _fusion_get_prompt(prompt_id)
    if not isinstance(prompt_id, str) or not prompt_id.strip():
        return None
    return next((item for item in _prompt_items() if item["id"] == prompt_id), None)
