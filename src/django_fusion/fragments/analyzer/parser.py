"""Static parser for Django template files.

Extracts:
- `{% extends "X" %}` -> template.extends
- `{% block NAME %}...{% endblock %}` -> template.blocks
- `{% comp "PATH" /%}` (self-closing), `{% comp "PATH" ... %}` (standalone),
  and `{% comp "PATH" ... %}...{% endcomp %}` (block-open) -> component uses

Drift-prone vs hooking into `django_fusion.comp.templatetags.tags.block` because
Django's template parser requires a live context. The regex approach here is
deliberately scoped to the canonical `{% comp %}` syntax documented in
`django_fusion/comp/README.md`.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field


# Self-closing: {% comp "path" key=val /%} -- terminator is "/ %}".
# `\s*` between the slash and "%}" accepts the canonical form (`/%}`)
# AND the whitespace-padded form (`/  %}`, `/ %}`) that the
# customizer chat template uses. Without this, the form silently
# fell through to the standalone matcher with the wrong `kind`.
COMP_SELF_CLOSING_RE = re.compile(
    r"""{%\s*comp\s+["']([^"']+)["']([^%]*?)/\s*%}""",
    re.DOTALL,
)

# Standalone open form: {% comp "path" key=val %} -- terminator is "%}".
# Common in the codebase (e.g. customizer fragments) -- no /%} AND no
# {% endcomp %} close. We treat these as legitimate single-line component
# invocations rather than silently skipping them.
COMP_STANDALONE_RE = re.compile(
    r"""{%\s*comp\s+["']([^"']+)["']([^%]*)%}""",
    re.DOTALL,
)

# Block-opening: {% comp "path" key=val %}...{% endcomp %} -- matches the
# FULL opener-to-endcomp span, so any opener registered here short-circuits
# the self_closing + standalone iterators (block wins on duplicates).
#
# CRITICAL: the body `(.*?)` is followed by `{% endcomp` -- the body must
# NOT cross other `{% comp` openers, otherwise block-form would silently
# swallow neighbouring standalone / self-closing forms (the regression
# case in `test_three_forms_in_one_file_dedup_returns_three`). The
# negative lookahead `(?:(?!{%\s*comp\b).)*?` forbids any `{% comp` token
# from appearing inside the body while still allowing `{% endcomp` to
# terminate it (`endcomp` has no `\b` boundary after `comp`).
COMP_BLOCK_RE = re.compile(
    r"""{%\s*comp\s+["']([^"']+)["']([^%]*)%}((?:(?!{%\s*comp\b).)*?){%\s*endcomp\s*%}""",
    re.DOTALL,
)

# Extends declaration: {% extends "X" %}
EXTENDS_RE = re.compile(r"""{%\s*extends\s+["']([^"']+)["']\s*%}""")

# Block declaration: {% block NAME %} or {% block NAME ... %}
BLOCK_RE = re.compile(r"""{%\s*block\s+([A-Za-z_][\w]*)([^%]*?)%}""")


# Section comment marker: {# @section: <name> #} -- analyzer-only, invisible
# at render time. The "@section:" keyword shoulder is required so plain
# visual separators like {# ---- Title ---- #} are NOT mistakenly
# treated as sections. Trailing "#}" closes the comment.
SECTION_COMMENT_RE = re.compile(
    r"""{#\s*@section:\s*(?P<name>[^\n#}]+?)\s*#}""",
)

# Section HTML wrapper: <tag data-section-id="<name>"> -- visible markup
# that the frontend can also target and that survives HTMX swaps. The
# attribute is case-insensitive; quotes may be single or double.
SECTION_HTML_RE = re.compile(
    r"""<\w[^>]*\bdata-section-id\s*=\s*["'](?P<name>[^"']+)["'][^>]*>""",
    re.IGNORECASE,
)


_KWARG_RE = re.compile(r"""([A-Za-z_]\w*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s]+))""")


def _lineno(content: str, pos: int) -> int:
    """Return the 1-based line number for ``pos`` in ``content``.

    Used to populate ``SectionMarker.line`` so callers can map sections
    back to source positions without re-counting characters themselves.

    Performance note: this is O(n) per call (counts ``\n`` between 0
    and ``pos``). For an N-template scan with M sections each this is
    O(N*M) total character-counting -- acceptable for typical
    template sizes but a future optimisation would build a single
    byte-offset -> line map per file once and reuse it across all
    sections in that scan.
    """
    return content.count("\n", 0, pos) + 1


def parse_kwargs(blob: str) -> dict[str, Any]:
    """Extract key=value kwargs from a tag argument blob (best-effort)."""
    out: dict[str, Any] = {}
    for m in _KWARG_RE.finditer(blob):
        key = m.group(1)
        if m.group(2) is not None:
            out[key] = m.group(2)
        elif m.group(3) is not None:
            out[key] = m.group(3)
        else:
            out[key] = m.group(4)
    return out


class CompUsage(BaseModel):
    path: str
    kind: str  # one of: self_closing | block | standalone
    kwargs: dict[str, Any] = Field(default_factory=dict)


class SectionMarker(BaseModel):
    """Raw section declaration extracted by the scanner.

    Distinct from the public ``schemas.Section`` so the parser stays
    stdlib-only and free of any dataclass-format dependency. The view
    layer raises ``SectionMarker`` into ``Section`` (with a stable slug
    built from the template path).
    """

    name: str
    marker_type: str  # one of: comment | html
    line: int


class ParsedTemplate(BaseModel):
    extends: str | None
    blocks: list[str]
    comps: list[CompUsage]
    sections: list[SectionMarker] = Field(default_factory=list)


def parse_template(content: str) -> ParsedTemplate:
    extends = None
    if (m := EXTENDS_RE.search(content)) is not None:
        extends = m.group(1)

    blocks = list({m.group(1) for m in BLOCK_RE.finditer(content)})

    # ---- Sections (analyzable concluded regions) ------------------------
    # Both forms are accepted. Dedup by name so duplicating partials (e.g.
    # reusing {% @section: Hero %} inside an include) doesn't grow the
    # list unbounded. First-seen marker_type wins; ordering is normalized
    # to source position so callers can map anchors back to the file.
    raw_sections: list[tuple[int, SectionMarker]] = []
    for m in SECTION_COMMENT_RE.finditer(content):
        name = m.group("name").strip()
        if not name:
            continue
        raw_sections.append(
            (m.start(), SectionMarker(name=name, marker_type="comment", line=_lineno(content, m.start())))
        )
    for m in SECTION_HTML_RE.finditer(content):
        name = m.group("name").strip()
        if not name:
            continue
        raw_sections.append(
            (m.start(), SectionMarker(name=name, marker_type="html", line=_lineno(content, m.start())))
        )

    raw_sections.sort(key=lambda x: x[0])
    # Dedup by name; HTML wrappers win over comment markers when both
    # forms exist for the same name -- HTML is "real" markup that the
    # frontend can also target, so it supersedes the documentation-only
    # comment form whenever both are present in the same template.
    seen_names: set[str] = set()
    has_html: set[str] = set()
    # ``html_lines`` records the line where each HTML wrapper sits so
    # the dedup loop can surface the HTML line when a name appears in
    # BOTH forms (the comment-form's line is the early seam, the
    # HTML-form's line is the real anchor; we always publish the
    # HTML line when HTML wins so consumers can jump to the markup).
    html_lines: dict[str, int] = {}
    for _pos, marker in raw_sections:
        if marker.marker_type == "html":
            has_html.add(marker.name)
            html_lines[marker.name] = marker.line
    sections: list[SectionMarker] = []
    for _pos, marker in raw_sections:
        if marker.name in seen_names:
            continue
        seen_names.add(marker.name)
        if marker.name in has_html:
            sections.append(
                SectionMarker(
                    name=marker.name,
                    marker_type="html",
                    line=html_lines[marker.name],
                )
            )
        else:
            sections.append(
                SectionMarker(
                    name=marker.name,
                    marker_type="comment",
                    line=marker.line,
                )
            )

    # Collect matches from all three iterators with their source-position,
    # then dedup by (path, opener_position) and sort by opener-position so
    # the result is in source order. The current iteration order
    # (block → self_closing → standalone) is preserved for dedup priority,
    # but the OUTPUT order is normalized to source-position. Without this
    # step, block matches further down the file would appear before
    # standalone matches earlier up -- which is technically correct but
    # surprising for callers (e.g. test_three_forms_in_one_file_dedup).
    seen: set[tuple[str, int]] = set()
    ordered: list[tuple[int, str, CompUsage]] = []  # (start, kind, usage)

    # 1. Block-form: longest match (opener → {% endcomp %}). Runs first
    #    so its opener is reserved before self_closing / standalone match.
    for m in COMP_BLOCK_RE.finditer(content):
        path = m.group(1)
        key = (path, m.start())
        if key in seen:
            continue
        seen.add(key)
        ordered.append(
            (
                m.start(),
                "block",
                CompUsage(
                    path=path,
                    kind="block",
                    kwargs=parse_kwargs(m.group(2) or ""),
                ),
            )
        )

    # 2. Self-closing: terminator is "/ %}". Skip if block reserved this opener.
    for m in COMP_SELF_CLOSING_RE.finditer(content):
        path = m.group(1)
        key = (path, m.start())
        if key in seen:
            continue
        seen.add(key)
        ordered.append(
            (
                m.start(),
                "self_closing",
                CompUsage(
                    path=path,
                    kind="self_closing",
                    kwargs=parse_kwargs(m.group(2) or ""),
                ),
            )
        )

    # 3. Standalone: terminator is "%}" (no /, no endcomp). Skip if seen.
    for m in COMP_STANDALONE_RE.finditer(content):
        path = m.group(1)
        key = (path, m.start())
        if key in seen:
            continue
        seen.add(key)
        ordered.append(
            (
                m.start(),
                "standalone",
                CompUsage(
                    path=path,
                    kind="standalone",
                    kwargs=parse_kwargs(m.group(2) or ""),
                ),
            )
        )

    # Normalize output to source order so callers get deterministic results
    # regardless of which regex iterator found each match.
    ordered.sort(key=lambda x: x[0])
    comps = [usage for _, _, usage in ordered]

    return ParsedTemplate(
        extends=extends,
        blocks=blocks,
        comps=comps,
        sections=sections,
    )
