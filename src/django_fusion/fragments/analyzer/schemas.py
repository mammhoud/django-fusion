"""Pydantic schemas for the analyzer output."""

from __future__ import annotations

import time
import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Prop(BaseModel):
    name: str
    type: str = "string"
    default: Any = None
    options: list[str] | None = None
    required: bool = False


class Slot(BaseModel):
    name: str
    description: str = ""


class Component(BaseModel):
    name: str
    path: str
    category: str = "UI"
    description: str = ""
    props: list[Prop] = Field(default_factory=list)
    slots: list[Slot] = Field(default_factory=list)
    # Phase 1.1 — skeleton / load-time metadata
    skeleton: str = Field(
        default="",
        description="Skeleton variant name (e.g. 'card', 'text-block', 'avatar'). "
        "Empty string means no skeleton override — use component default.",
    )
    skeleton_config: dict[str, Any] = Field(
        default_factory=dict,
        description="Per-component skeleton overrides: min_height, animate, "
        "delay_ms, repeat_count, etc. Keys are forward-compatible; unknown keys "
        "are ignored by the skeleton renderer.",
    )

    def to_dict(self) -> dict[str, Any]:
        data = self.model_dump()
        data["id"] = _id("comp")
        return data


class Block(BaseModel):
    name: str
    description: str = ""
    optional: bool = False


class Section(BaseModel):
    """A logical, named, analyzable region inside a template.

    Sections are declared with EITHER:

    1. Django ``{# @section: <name> #}`` comments (analyzer-only marker —
       invisible at render time); or
    2. HTML wrappers carrying ``data-section-id="<name>"`` (visible markup
       that the frontend can also target; survives HTMX swaps cleanly).

    The analyzer scans both forms and emits a flat ordered list keyed by
    name. Duplicate names within the same template are collapsed to one
    entry so analyzers don't grow unbounded under partial reuse.

    ``marker_type`` records which form produced each entry, so documentation
    tooling can surface "marker drift" (HTML wrapper vs comment-only) as
    its own report.

    Identity is stable across commits: ``id = sec--<path_slug>--<name_slug>``,
    so reruns and diffs line up deterministically without UUIDs.
    """

    name: str
    id: str
    marker_type: Literal["comment", "html"]
    line: int = 0


class Template(BaseModel):
    name: str
    path: str
    category: str = "Layout"
    extends: str | None = None
    blocks: list[Block] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = self.model_dump()
        data["id"] = _id("tpl")
        return data


class PageComponentUsage(BaseModel):
    component_id: str
    props: dict[str, Any] = Field(default_factory=dict)
    # Phase 1.1 — DOM-order position for skeleton placeholder rendering.
    # The analyzer emits components in scan-order (file position).
    # skeleton_order is assigned by a post-processor that walks the
    # template's rendered DOM tree so the frontend can render skeleton
    # placeholders in the same visual order the user sees.
    skeleton_order: int = Field(default=0, ge=0)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class Page(BaseModel):
    title: str
    path: str
    template: str | None = None
    components: list[PageComponentUsage] = Field(default_factory=list)
    # Phase 1.1 — asset dependency & load-priority metadata.
    # Populated by the webpack-manifest post-processor after the initial
    # scan so the frontend can preload / lazy-load the right bundles.
    dependencies: list[str] = Field(
        default_factory=list,
        description="Webpack chunk names (CSS/JS) required by this page. "
        "Resolved from bundles.json by the post-processor.",
    )
    load_priority: str = Field(
        default="auto",
        description="Loading strategy: 'critical' (preload), 'eager' (sync load), "
        "'lazy' (defer), 'auto' (heuristic based on viewport position).",
    )

    def to_dict(self) -> dict[str, Any]:
        data = self.model_dump()
        data["id"] = _id("page")
        return data


class AnalyzeRequest(BaseModel):
    website_slug: str | None = None
    url: str | None = None
    include_components: bool = True
    include_templates: bool = True
    depth: int = 3
    filters: dict[str, Any] = Field(default_factory=dict)

    # NOTE: construction is now exclusively done via keyword arguments after
    # the caller (the AnalyzeView) has validated/coerced each field. A
    # from_payload() classmethod was removed because it duplicated coercion
    # logic and re-introduced the unsafe un-capped int() bug. Construct
    # AnalyzeRequest directly.


def website_header(slug: str | None, url: str | None, name: str | None) -> dict[str, Any]:
    return {
        "name": name or (slug or "Website"),
        "slug": slug or "default",
        "base_url": url or "",
        "analyzed_at": _now_iso(),
    }
