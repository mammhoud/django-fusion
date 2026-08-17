"""Tests for structured website/webapp enhancement MCP tools."""

import pytest
from django_fusion.plugins.designer.tools import MCP_DESIGNER_TOOLS
from django_fusion.plugins.designer.website import (
    designer_webapp_enhancement_plan,
    designer_website_audit,
)

SECTIONS = [
    {
        "name": "Hero",
        "kind": "hero",
        "layout": "split",
        "has_visual": True,
        "has_cta": True,
        "text_words": 22,
        "interactive_states": ["success", "error", "empty", "loading", "motion"],
    },
    {
        "name": "Features",
        "layout": "asymmetric-grid",
        "has_visual": True,
        "mobile_strategy": "stack",
        "interactive_states": ["success", "error", "empty", "loading"],
    },
    {
        "name": "Proof",
        "layout": "quote",
        "has_visual": True,
        "mobile_strategy": "stack",
        "interactive_states": ["success", "error", "empty", "loading"],
    },
]


def test_website_audit_returns_structured_findings_and_score():
    result = designer_website_audit(
        "precis-landing",
        SECTIONS,
        accessibility_reviewed=True,
        real_assets_available=True,
        cta_intents=["signup", "contact"],
    )

    assert 0 <= result["scores"]["overall"] <= 100
    assert result["project"] == "precis-landing"
    assert isinstance(result["findings"], list)
    assert result["guidance"]["surface"]


def test_website_audit_catches_accessibility_and_mobile_gaps():
    result = designer_website_audit(
        "precis",
        [{"name": "Course grid", "is_multi_column": True}],
        required_features=["course discovery"],
    )

    categories = {finding["category"] for finding in result["findings"]}
    assert "accessibility" in categories
    assert "responsive" in categories
    assert "product" in categories


def test_website_audit_rejects_malformed_section_metadata():
    with pytest.raises(ValueError, match="interactive_states"):
        designer_website_audit(
            "precis-landing",
            [{"name": "Hero", "interactive_states": "loading"}],
        )
    with pytest.raises(ValueError, match="text_words"):
        designer_website_audit(
            "precis-landing",
            [{"name": "Hero", "text_words": -1}],
        )


def test_website_audit_accepts_any_project_and_rejects_unbounded_values():
    # Any project is now accepted (validation removed — designer is project-agnostic)
    result = designer_website_audit("hello-world", SECTIONS)
    assert result["project"] == "hello-world"
    with pytest.raises(ValueError, match="design_variance"):
        designer_website_audit("formint", SECTIONS, design_variance=11)


def test_enhancement_plan_is_ordered_and_never_applies_changes():
    result = designer_webapp_enhancement_plan(
        project="formint",
        surface="webapp",
        sections=SECTIONS,
        accessibility_reviewed=True,
        real_assets_available=True,
    )

    assert [phase["order"] for phase in result["phases"]] == [1, 2, 3, 4]
    assert result["apply_required"] is True
    assert result["deployment_required"] is True
    assert any("project-specific" in task for task in result["phases"][1]["tasks"])


def test_website_tools_are_read_only_and_registered():
    assert "designer.website_audit" in MCP_DESIGNER_TOOLS
    assert "designer.webapp_enhancement_plan" in MCP_DESIGNER_TOOLS
    for name in ("designer.website_audit", "designer.webapp_enhancement_plan"):
        tool = MCP_DESIGNER_TOOLS[name]
        assert tool["inputSchema"]["type"] == "object"
        assert tool["annotations"]["readOnlyHint"] is True
        assert tool["annotations"]["destructiveHint"] is False
