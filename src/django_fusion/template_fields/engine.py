"""
django_fusion.template_fields.engine
====================================

Sandboxed dynamic template field engine.

Renders user-authored templates containing ``{{ customer.name }}`` style
placeholders against live data. The engine is deliberately **not** a Django
or Jinja2 template engine: templates are regex-parsed into field references,
resolved through dotted-path traversal with an allowlist, transformed by the
filter registry, HTML-escaped, and assembled. There is no ``eval``/``exec``,
no method invocation, and no arbitrary attribute access — unresolved values
fail safe to a fallback or empty string.

Rendering pipeline (see ``docs/features/template-fields/``):

    Parse → Resolve → Validate → Escape → Format → Assemble → Preview
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Any

from django.utils.safestring import SafeString, mark_safe

from django_fusion.template_fields.filters import (
    MISSING,
    FilterRegistry,
    default_registry,
)

#: ``{{ path|filter:"arg"|filter2 }}`` — a dotted path plus optional filters.
#: Filter args are double-quoted strings or bare tokens (``truncate:30``).
TOKEN_RE = re.compile(
    r"\{\{\s*"
    r"(?P<path>[A-Za-z_][A-Za-z0-9_.]*)"
    r"(?P<filters>(?:\s*\|\s*[A-Za-z_][A-Za-z0-9_]*(?:\s*:\s*(?:\"(?:\\.|[^\"])*\"|[A-Za-z0-9_.\-]+))?)*)"
    r"\s*\}\}"
)

#: One filter segment: ``|name``, ``|name:"arg"``, or ``|name:arg``.
FILTER_SEGMENT_RE = re.compile(
    r"\|\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s*:\s*(?:\"(?P<arg>(?:\\.|[^\"])*)\"|(?P<arg_bare>[A-Za-z0-9_.\-]+)))?"
)


@dataclass(frozen=True)
class FilterSpec:
    """One parsed filter on a field reference (name + optional string arg)."""

    name: str
    arg: str | None = None


@dataclass(frozen=True)
class FieldReference:
    """A parsed ``{{ path|filters }}`` occurrence in a template."""

    path: str
    root: str
    filters: tuple[FilterSpec, ...]
    raw: str
    position: int


@dataclass
class ValidationIssue:
    """A validation finding about a template or its resolution."""

    level: str  # INFO | WARNING | ERROR
    code: str
    message: str
    path: str | None = None


@dataclass
class PreviewResult:
    """Result of a preview render — html plus resolution diagnostics."""

    html: str
    issues: list[ValidationIssue] = field(default_factory=list)
    resolved: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)


def _get_child(value: Any, key: str) -> Any:
    """Resolve one dotted-path segment against a value (never calls methods)."""
    if value is MISSING or value is None:
        return MISSING
    if isinstance(value, dict):
        return value.get(key, MISSING)
    if isinstance(value, (list, tuple)):
        try:
            index = int(key)
        except (TypeError, ValueError):
            return MISSING
        if 0 <= index < len(value):
            return value[index]
        return MISSING
    if isinstance(value, SafeString):
        return MISSING
    # Attribute access only — callables are never invoked and never resolved
    # (a bound method is not data; rendering its repr would leak internals).
    if hasattr(value, key):
        attr = getattr(value, key)
        if callable(attr) and not isinstance(attr, type):
            return MISSING
        return attr
    return MISSING


def resolve_path(context: dict[str, Any], path: str, allowlist: set[str] | None) -> Any:
    """Resolve a dotted path against context, enforcing the root allowlist.

    Returns ``MISSING`` when any segment cannot be resolved. Accessing a
    root that is not in ``allowlist`` (when provided) is treated as missing.
    """
    parts = path.split(".")
    root = parts[0]
    if allowlist is not None and root not in allowlist:
        return MISSING
    value = context.get(root, MISSING)
    for part in parts[1:]:
        value = _get_child(value, part)
        if value is MISSING:
            break
    return value


def parse_fields(template: str, *, registry: FilterRegistry | None = None) -> list[FieldReference]:
    """Parse every field reference in a template string."""
    registry = registry or default_registry()
    refs: list[FieldReference] = []
    for match in TOKEN_RE.finditer(template):
        path = match.group("path")
        filters: list[FilterSpec] = []
        for segment in FILTER_SEGMENT_RE.finditer(match.group("filters")):
            name = segment.group("name")
            arg = segment.group("arg")
            if arg is None:
                arg = segment.group("arg_bare")
            if arg is not None:
                arg = arg.replace(r"\"", '"').replace(r"\\", "\\")
            filters.append(FilterSpec(name=name, arg=arg))
        refs.append(
            FieldReference(
                path=path,
                root=path.split(".")[0],
                filters=tuple(filters),
                raw=match.group(0),
                position=match.start(),
            )
        )
    return refs


class TemplateFieldEngine:
    """Sandboxed dynamic template renderer.

    Args:
        registry: Filter registry to use (defaults to the shared registry).
        max_string_length: Hard cap on any single resolved string value.
        max_list_items: Hard cap on any resolved list/tuple length.
        auto_escape: HTML-escape resolved values by default (True).
    """

    def __init__(
        self,
        *,
        registry: FilterRegistry | None = None,
        max_string_length: int = 10_000,
        max_list_items: int = 100,
        auto_escape: bool = True,
    ) -> None:
        self.registry = registry or default_registry()
        self.max_string_length = max_string_length
        self.max_list_items = max_list_items
        self.auto_escape = auto_escape

    # ── public API ─────────────────────────────────────────────────────────

    def resolve_fields(self, template: str) -> list[FieldReference]:
        """Return the parsed field references in a template."""
        return parse_fields(template, registry=self.registry)

    def render(
        self,
        template: str,
        context: dict[str, Any],
        *,
        allowlist: set[str] | list[str] | None = None,
        auto_escape: bool | None = None,
    ) -> str:
        """Render a template, resolving every field against ``context``.

        Unresolved fields fail safe: they render as ``""`` (or the ``default``
        filter's fallback when present). Unknown filters raise ``KeyError`` so
        authoring mistakes surface loudly in validation/preview.
        """
        allow = _normalize_allowlist(allowlist)
        escape = self.auto_escape if auto_escape is None else auto_escape
        parts: list[str] = []
        last = 0
        for ref in parse_fields(template, registry=self.registry):
            parts.append(template[last : ref.position])
            value = self._resolve_one(ref, context, allow)
            parts.append(self._render_value(value, escape))
            last = ref.position + len(ref.raw)
        parts.append(template[last:])
        return "".join(parts)

    def validate(
        self,
        template: str,
        *,
        context: dict[str, Any] | None = None,
        allowlist: set[str] | list[str] | None = None,
    ) -> list[ValidationIssue]:
        """Validate a template: syntax, filter names, and (optionally) roots.

        Unknown filters are ``ERROR``; missing allowlisted roots are
        ``WARNING`` (they may be provided at render time); unresolved fields
        against ``context`` are ``WARNING``.
        """
        issues: list[ValidationIssue] = []
        allow = _normalize_allowlist(allowlist)
        for ref in parse_fields(template, registry=self.registry):
            for spec in ref.filters:
                if self.registry.get(spec.name) is None:
                    issues.append(
                        ValidationIssue(
                            level="ERROR",
                            code="unknown_filter",
                            message=f"Unknown filter {spec.name!r} in {ref.raw}",
                            path=ref.path,
                        )
                    )
            if allow is not None and ref.root not in allow:
                issues.append(
                    ValidationIssue(
                        level="WARNING",
                        code="blocked_root",
                        message=f"Root {ref.root!r} is not in the allowlist ({ref.raw})",
                        path=ref.path,
                    )
                )
            if context is not None and resolve_path(context, ref.path, allow) is MISSING:
                issues.append(
                    ValidationIssue(
                        level="WARNING",
                        code="unresolved",
                        message=f"Could not resolve {ref.path!r} ({ref.raw})",
                        path=ref.path,
                    )
                )
        return issues

    def preview(
        self,
        template: str,
        context: dict[str, Any],
        *,
        allowlist: set[str] | list[str] | None = None,
    ) -> PreviewResult:
        """Render against sample data and report resolution diagnostics."""
        allow = _normalize_allowlist(allowlist)
        resolved: list[str] = []
        unresolved: list[str] = []
        issues = self.validate(template, context=context, allowlist=allow)

        def _replacer(ref: FieldReference) -> str:
            value = self._resolve_one(ref, context, allow)
            if value is MISSING:
                unresolved.append(ref.path)
            else:
                resolved.append(ref.path)
            return self._render_value(value, self.auto_escape)

        parts: list[str] = []
        last = 0
        for ref in parse_fields(template, registry=self.registry):
            parts.append(template[last : ref.position])
            parts.append(_replacer(ref))
            last = ref.position + len(ref.raw)
        parts.append(template[last:])
        return PreviewResult(html="".join(parts), issues=issues, resolved=resolved, unresolved=unresolved)

    # ── internals ───────────────────────────────────────────────────────────

    def _resolve_one(self, ref: FieldReference, context: dict[str, Any], allow: set[str] | None) -> Any:
        value = resolve_path(context, ref.path, allow)
        # Bound list/tuple values before filters run so ``join``/``length``
        # operate on the capped collection, not the full one.
        if isinstance(value, (list, tuple)):
            value = self._bounded_list(value)
        for spec in ref.filters:
            func = self.registry.get(spec.name)
            if func is None:
                raise KeyError(f"Unknown filter: {spec.name}")
            args = (spec.arg,) if spec.arg is not None else ()
            value = func(value, args)
        return value

    def _render_value(self, value: Any, escape: bool) -> str:
        if value is MISSING or value is None:
            return ""
        if isinstance(value, SafeString):
            return str(value)
        if isinstance(value, str):
            value = value[: self.max_string_length]
        text = str(value)
        if not escape:
            return text
        return html.escape(text, quote=True)

    def _bounded_list(self, value: list | tuple) -> list | tuple:
        if len(value) > self.max_list_items:
            return value[: self.max_list_items]
        return value


def _normalize_allowlist(allowlist: set[str] | list[str] | None) -> set[str] | None:
    if allowlist is None:
        return None
    return {str(item) for item in allowlist}


__all__ = [
    "FieldReference",
    "FilterSpec",
    "PreviewResult",
    "TemplateFieldEngine",
    "ValidationIssue",
    "parse_fields",
    "resolve_path",
    "mark_safe",
]
