"""Dataclass schemas for the analyzer output.

Pure stdlib (no Pydantic) so `django_fusion.analyzer` adds no third-party
dependency burden to the foundation library.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Literal


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class Prop:
    name: str
    type: str = "string"
    default: Any = None
    options: list[str] | None = None
    required: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["options"] = d["options"] or None
        return d


@dataclass
class Slot:
    name: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Component:
    name: str
    path: str
    category: str = "UI"
    description: str = ""
    props: list[Prop] = field(default_factory=list)
    slots: list[Slot] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": _id("comp"),
            "name": self.name,
            "path": self.path,
            "category": self.category,
            "description": self.description,
            "props": [p.to_dict() for p in self.props],
            "slots": [s.to_dict() for s in self.slots],
        }


@dataclass
class Block:
    name: str
    description: str = ""
    optional: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Section:
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Template:
    name: str
    path: str
    category: str = "Layout"
    extends: str | None = None
    blocks: list[Block] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": _id("tpl"),
            "name": self.name,
            "path": self.path,
            "category": self.category,
            "extends": self.extends,
            "blocks": [b.to_dict() for b in self.blocks],
            "sections": [s.to_dict() for s in self.sections],
        }


@dataclass
class PageComponentUsage:
    component_id: str
    props: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Page:
    title: str
    path: str
    template: str | None = None
    components: list[PageComponentUsage] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": _id("page"),
            "title": self.title,
            "path": self.path,
            "template": self.template,
            "components": [c.to_dict() for c in self.components],
        }


@dataclass
class AnalyzeRequest:
    website_slug: str | None = None
    url: str | None = None
    include_components: bool = True
    include_templates: bool = True
    depth: int = 3
    filters: dict[str, Any] = field(default_factory=dict)

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
