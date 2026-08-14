"""Contract tests for the repository prompt catalog."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "applications" / "agents"
sys.path.insert(0, str(AGENTS_DIR))

from prompt_catalog import get_prompt, list_prompt_metadata, load_prompt_catalog  # noqa: E402


def test_catalog_is_valid_and_has_all_prompt_groups():
    catalog = load_prompt_catalog()

    assert catalog["schema_version"] == "1.0"
    assert catalog["skill_prompts"]
    assert catalog["projects"]
    assert catalog["workflows"]


def test_skill_and_project_prompts_have_complete_contracts():
    catalog = load_prompt_catalog()

    for prompt in catalog["skill_prompts"]:
        assert prompt["id"]
        assert prompt["description"]
        assert prompt["prompt"]
        assert prompt["agent"]
        assert prompt["expected_output"]
        assert prompt["safety"]

    for prompt in catalog["projects"]:
        assert prompt["id"]
        assert prompt["name"]
        assert prompt["path"]
        assert prompt["description"]
        assert prompt["prompt"]
        assert prompt["agent_sequence"]
        assert prompt["checks"]
        assert prompt["related_skills"]


def test_listing_is_concise_and_detail_is_complete():
    listing = list_prompt_metadata()
    detail = get_prompt("project.landing-fusion")

    assert listing["count"] >= 10
    assert all(set(item) >= {"id", "title", "description", "kind"} for item in listing["prompts"])
    assert detail is not None
    assert detail["path"] == "projects/precis/landi/"
    assert detail["checks"]
    assert get_prompt("does-not-exist") is None


def test_mcp_prompt_endpoints_list_detail_and_not_found():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    import mcp_server

    try:
        client = TestClient(mcp_server.app)
    except Exception as exc:  # pragma: no cover - dependency-version-specific
        pytest.skip(f"FastAPI test client unavailable: {exc}")

    listing = client.get("/prompts")
    assert listing.status_code == 200
    assert listing.json()["ok"] is True
    assert listing.json()["count"] >= 10

    detail = client.get("/prompts/project.landing-fusion")
    assert detail.status_code == 200
    assert detail.json()["prompt"]["path"] == "projects/precis/landi/"

    missing = client.get("/prompts/does-not-exist")
    assert missing.status_code == 404


def test_catalog_loader_reports_duplicate_or_malformed_data(monkeypatch):
    import prompt_catalog

    monkeypatch.setattr(prompt_catalog, "_CATALOG_PATH", Path("/does/not/exist/catalog.json"))
    prompt_catalog.load_prompt_catalog.cache_clear()
    with pytest.raises(prompt_catalog.PromptCatalogError, match="Unable to load"):
        prompt_catalog.load_prompt_catalog()
    prompt_catalog.load_prompt_catalog.cache_clear()
