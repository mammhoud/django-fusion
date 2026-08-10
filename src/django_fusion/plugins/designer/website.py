"""Structured website/webapp audit helpers for the django-fusion MCP designer.

This module turns the repository's frontend/design guidance into deterministic
recommendations. It accepts a bounded description of a project surface rather
than fetching URLs or reading arbitrary files, so it is safe to expose through
an authenticated MCP endpoint.
"""

from __future__ import annotations

import math
from typing import Any

from django_fusion.plugins.designer.handlers import _bounded_list, _text

_DEFAULT_GUIDANCE = {
    "surface": "web surface",
    "focus": ["content clarity", "user journey", "accessibility", "project-owned assets"],
}


def _project_guidance(project: str) -> dict[str, Any]:
    """Resolve project guidance from django-fusion settings or return a sensible default.

    Projects can customise this by defining ``FUSION_AUDIT_GUIDANCE`` in their Django
    settings. When no custom guidance is configured the function returns a generic
    default that applies to any web surface."""
    try:
        from django.conf import settings
        custom = getattr(settings, "FUSION_AUDIT_GUIDANCE", {}) or {}
        if isinstance(custom, dict) and project in custom:
            return custom[project]
    except Exception:
        pass
    return dict(_DEFAULT_GUIDANCE)


def _finding(
    category: str,
    severity: str,
    message: str,
    recommendation: str,
    *,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "category": category,
        "severity": severity,
        "message": message,
        "recommendation": recommendation,
        "evidence": evidence or {},
    }


def _state_values(value: Any) -> set[str]:
    if value is None:
        return set()
    if not isinstance(value, list):
        raise ValueError("interactive_states must be an array")
    return {_text(item, limit=40).lower() for item in value}


def _word_count(value: Any) -> int:
    try:
        count = int(value or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("text_words must be an integer") from exc
    if count < 0:
        raise ValueError("text_words must be >= 0")
    return count


def _section_values(sections: list[Any]) -> list[dict[str, Any]]:
    normalized = []
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError("each section must be an object")
        normalized.append(
            {
                "name": _text(section.get("name"), default="Unnamed section", limit=100),
                "kind": _text(section.get("kind"), default="content", limit=50),
                "layout": _text(section.get("layout"), default="stack", limit=50),
                "has_visual": bool(section.get("has_visual", False)),
                "has_cta": bool(section.get("has_cta", False)),
                "has_eyebrow": bool(section.get("has_eyebrow", False)),
                "is_multi_column": bool(section.get("is_multi_column", False)),
                "mobile_strategy": _text(section.get("mobile_strategy"), limit=50),
                "interactive_states": _state_values(section.get("interactive_states", [])),
                "text_words": _word_count(section.get("text_words", 0)),
            }
        )
    return normalized


def designer_website_audit(
    project: str,
    sections: list[dict[str, Any]],
    *,
    surface: str = "website",
    audience: str = "general audience",
    vibe: str = "clear and premium",
    design_variance: int = 7,
    motion_intensity: int = 4,
    visual_density: int = 4,
    dark_mode: bool = True,
    accessibility_reviewed: bool = False,
    real_assets_available: bool = False,
    cta_intents: list[str] | None = None,
    required_features: list[str] | None = None,
) -> dict[str, Any]:
    """Audit structured website metadata against the frontend skill rules."""
    project = _text(project, limit=40).lower()
    if not project:
        raise ValueError("project is required")
    surface = _text(surface, default="website", limit=40).lower()
    if surface not in {"website", "webapp", "landing", "catalog", "dashboard"}:
        raise ValueError("surface must be website, webapp, landing, catalog, or dashboard")
    for name, value in {
        "design_variance": design_variance,
        "motion_intensity": motion_intensity,
        "visual_density": visual_density,
    }.items():
        if not isinstance(value, int) or not 1 <= value <= 10:
            raise ValueError(f"{name} must be an integer from 1 to 10")

    sections = _section_values(_bounded_list(sections, label="sections"))
    if not sections:
        raise ValueError("sections must contain at least one page section")
    cta_intents = [_text(item, limit=50).lower() for item in _bounded_list(cta_intents, label="cta_intents")]
    required_features = [_text(item, limit=80) for item in _bounded_list(required_features, label="required_features")]

    findings: list[dict[str, Any]] = []
    hero = next((section for section in sections if section["kind"] == "hero"), None)
    if hero is None:
        findings.append(_finding("content", "high", "The page has no identified hero section.", "Define one focused value proposition, one primary CTA, and one real visual."))
    elif hero["text_words"] > 60:
        findings.append(_finding("content", "medium", "The hero copy is likely too dense for the first viewport.", "Reduce the hero to a short headline, concise subtext, and one primary CTA.", evidence={"text_words": hero["text_words"]}))
    if hero and not hero["has_visual"] and surface in {"website", "landing", "catalog"}:
        findings.append(_finding("assets", "medium", "The hero has no declared visual asset.", "Use an existing brand asset, generated image, or an explicit placeholder slot instead of a fake CSS screenshot."))

    eyebrow_count = sum(section["has_eyebrow"] for section in sections)
    eyebrow_limit = max(1, math.ceil(len(sections) / 3))
    if eyebrow_count > eyebrow_limit:
        findings.append(_finding("composition", "medium", "Too many section eyebrows create repetitive template rhythm.", "Keep at most one eyebrow per three sections and let focused headlines carry the hierarchy.", evidence={"count": eyebrow_count, "recommended_max": eyebrow_limit}))

    layouts = [section["layout"] for section in sections]
    repeated_layouts = sorted({layout for layout in layouts if layouts.count(layout) > 1})
    if repeated_layouts and design_variance > 4:
        findings.append(_finding("composition", "medium", "Several sections reuse the same layout family.", "Vary the composition with a full-width statement, asymmetric grid, media-led section, or interactive block.", evidence={"repeated_layouts": repeated_layouts}))

    for section in sections:
        if section["is_multi_column"] and not section["mobile_strategy"]:
            findings.append(_finding("responsive", "high", f"{section['name']} has columns but no mobile strategy.", "Declare the mobile collapse, ordering, and touch behavior in the component itself.", evidence={"section": section["name"]}))
        if section["is_multi_column"] and surface in {"webapp", "dashboard"} and section["mobile_strategy"] == "stack" and visual_density >= 7:
            findings.append(_finding("responsive", "medium", f"{section['name']} may lose data clarity when stacked.", "Use a deliberate compact table, horizontal scroll, or prioritized mobile subset rather than blindly stacking dense columns.", evidence={"section": section["name"]}))
        if section["interactive_states"] and not {"loading", "error", "empty"}.issubset(section["interactive_states"]):
            findings.append(_finding("interaction", "medium", f"{section['name']} is missing a complete interaction state cycle.", "Add loading, empty, error, success, and reduced-motion behavior as applicable.", evidence={"section": section["name"], "states": sorted(section["interactive_states"])}))

    if motion_intensity > 3 and not any("motion" in section["interactive_states"] for section in sections):
        findings.append(_finding("motion", "low", "The requested motion intensity is not represented in the section metadata.", "Use purposeful reveal or feedback motion, honor prefers-reduced-motion, and avoid scroll listeners in React."))
    if not accessibility_reviewed:
        findings.append(_finding("accessibility", "high", "Accessibility review is not recorded.", "Check heading order, keyboard flow, focus states, contrast, labels, reduced motion, and touch targets before release."))
    if not dark_mode and surface in {"website", "webapp", "catalog", "dashboard"}:
        findings.append(_finding("theme", "low", "Dual-theme behavior is not enabled or documented.", "Add a deliberate light/dark strategy unless the product explicitly requires one fixed theme."))
    if not real_assets_available and surface in {"website", "landing", "catalog"}:
        findings.append(_finding("assets", "medium", "No real visual assets are declared for a visual web surface.", "Audit existing project-owned logos, photography, screenshots, and generated asset slots before polishing CSS."))

    normalized_ctas = [intent for intent in cta_intents if intent]
    duplicate_ctas = sorted({intent for intent in normalized_ctas if normalized_ctas.count(intent) > 1})
    if duplicate_ctas:
        findings.append(_finding("conversion", "medium", "Multiple CTAs share the same intent.", "Choose one consistent label per intent and reuse it across navigation, hero, and footer.", evidence={"duplicate_intents": duplicate_ctas}))

    if required_features and not any(f.lower().startswith(project) for f in required_features):
        findings.append(_finding("product", "low", f"Verify that required_features cover the core {project} product surface.", "Add project-specific feature requirements before proceeding with the enhancement plan.", evidence={"required_features": required_features}))

    severity_weight = {"high": 3, "medium": 2, "low": 1}
    penalty = sum(severity_weight[item["severity"]] for item in findings)
    score = max(0, min(100, 100 - penalty * 6))
    return {
        "project": project,
        "surface": surface,
        "audience": _text(audience, default="general audience", limit=120),
        "vibe": _text(vibe, default="clear and premium", limit=120),
        "scores": {"overall": score, "finding_count": len(findings), "high_priority": sum(item["severity"] == "high" for item in findings)},
        "guidance": _project_guidance(project),
        "findings": findings,
        "next_steps": [
            "Resolve high-priority accessibility, responsive, and content findings first.",
            "Preview registered components through designer.preview with non-sensitive JSON props.",
            "Apply code changes only through the owning project's reviewed development workflow.",
        ],
    }


def designer_webapp_enhancement_plan(**kwargs: Any) -> dict[str, Any]:
    """Return an ordered, read-only implementation plan from a website audit."""
    audit = designer_website_audit(**kwargs)
    project = audit["project"]
    phases = [
        {"order": 1, "name": "Foundation", "tasks": ["Confirm project-owned design tokens, fonts, logo fallback, asset paths, and theme strategy.", "Remove duplicate or unreachable template paths before adding new UI."]},
        {"order": 2, "name": "Content and structure", "tasks": ["Clarify the primary user journey and page hierarchy.", "Keep hero copy concise and use varied section compositions."]},
        {"order": 3, "name": "Interaction and components", "tasks": ["Reuse the django-fusion component registry, forms, tables, and Wagtail blocks.", "Implement loading, empty, error, success, keyboard, and reduced-motion states."]},
        {"order": 4, "name": "Verification", "tasks": ["Run project checks, template tests, frontend build, accessibility review, and browser smoke tests.", "Review generated changes manually before merge or deployment."]},
    ]
    guidance = _project_guidance(project)
    phases[1]["tasks"].append(
        "Verify project-specific journeys, content, and workflows "
        f"according to the {project} product surface."
    )
    return {"audit": audit, "phases": phases, "apply_required": True, "deployment_required": True}
