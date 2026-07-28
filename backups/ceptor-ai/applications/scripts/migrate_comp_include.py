#!/usr/bin/env python3
"""
One-shot Django-template-tag-aware transformer. NOT shipped to production.

Rewrites:
  * literal   `{% include "path" with k=v only %}` -> `{% comp "path" k=v only / %}`
  * literal   `{% include 'path' with k=v only %}`  -> `{% comp 'path' k=v only / %}`
  * literal   `{% include "path" %}`                -> `{% comp "path" / %}`
  *           `{% comp_include "path" k=v only %}`  -> `{% comp "path" k=v only / %}`
  *           `{% comp_include "path" %}`           -> `{% comp "path" / %}`

Preserves verbatim:
  * dynamic `{% include var %}` and `{% include foo.bar %}` -- per AGENTS.md,
    these stay as raw include (comp_only supports literal path names).
  * comment blocks (`{# ... #}`) containing the syntax above -- docs unchanged.
  * existing `{% comp %}` usages (this script does not touch them).

Idempotent: re-running on an already-migrated file is a no-op.

Usage:
    python3 migrate_comp_include.py FILE_OR_DIR [FILE_OR_DIR ...]
    python3 migrate_comp_include.py --root applications

Reports per file: lines scanned, lines changed, kind of change.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Skip dirs that are vendored noise / generated artifacts / non-Django templates.
SKIP_DIR_NAMES = {
    "node_modules", ".git", ".venv", "venv", "__pycache__",
    "staticfiles", "media", "bundles", "dist", "build",
    ".mypy_cache", ".ruff_cache", "logs",
}

# Bind to: {% include "literal" %} or {% include 'literal' %} (literal only)
# Group 1: quote ( " or ' )
# Group 2: path body
# Group 3: trailing rest (after the literal -- includes "with k=v only %}")
# The optional "[with|kwargs|" segment lets us detect and rewrite.
#
# We deliberately do NOT match dynamic include like `{% include foo %}
# because dynamic names must keep the {% include %} form (comp does not
# resolve variables at parse time and IncludePathComponent.from_include_path
# is path-keyed). Per AGENTS.md, dynamic includes stay as {% include %}.
INCLUDE_LITERAL_RE = re.compile(
    r"""\{%[-\s]*
        include                                # tag name
        \s+['"]([^'"]+)['"]                    # quoted literal path (capture)
        (                                      # group 3: optional kwargs + only
            \s+
            (?: with \s+)?
            (?P<kwonly>[\s\S]*?)
        )?
        \s*[-\s]*%\}""",
    re.VERBOSE,
)

COMP_INCLUDE_LITERAL_RE = re.compile(
    r"""\{%[-\s]*
        comp_include                           # tag name
        \s+['"]([^'"]+)['"]                    # quoted literal path (capture)
        (                                      # group 2: kwargs + only
            \s+(?P<kwonly>[\s\S]*?)
        )?
        \s*[-\s]*%\}""",
    re.VERBOSE,
)

# `with` keyword at start of following tail is stripped (comp has no `with`).
WITH_RE = re.compile(r"\s*\bwith\b\s+")


# Two comment-block grammars are honored as protected regions:
#   1. Inline  `{# ... #}`  (single-line preferred but multi-line tolerated).
#   2. Block   `{% comment %} ... {% endcomment %}`  (Django block comment).
# We split the text into "outside" / "inside" chunks around these regions so
# transform_subn is never applied to text inside a comment. `COMMENT_BLOCK_RE`
# matches the Django `{% comment %}...{% endcomment %}` pair (lazy on the body).
COMMENT_SPLIT_RE = re.compile(
    r"(\{#[\s\S]*?#\}|\{\%\s*comment\s*\%\}[\s\S]*?\{\%\s*endcomment\s*\%\})"
)


def split_outside_comments(text: str) -> list[tuple[str, bool]]:
    """Return ``[(chunk, in_comment_region), ...]`` pairs.

    The empty/in-comment regions keep their content verbatim so callers
    decide whether to rewrite them (default: skip).
    """
    parts: list[tuple[str, bool]] = []
    last = 0
    for m in COMMENT_SPLIT_RE.finditer(text):
        if m.start() > last:
            parts.append((text[last:m.start()], False))
        parts.append((m.group(0), True))
        last = m.end()
    if last < len(text):
        parts.append((text[last:], False))
    return parts


def transform_include_literal(text: str, *, in_comments: bool = False) -> tuple[str, int]:
    """Rewrite literal `{% include "X" %}` calls into `{% comp "X" / %}`.

    When ``in_comments=False`` (default), skips text inside `{# ... #}`
    inline comments AND inside `{% comment %}...{% endcomment %}` block
    comments — those are documentation examples, not live includes.
    Set ``in_comments=True`` to rewrite inside comment regions too --
    e.g. to update stale documentation after removing a tag.
    """
    count = 0
    out: list[str] = []
    for chunk, in_comment_region in split_outside_comments(text):
        # Rewrite active code always. Rewrite inside-comment regions ONLY
        # when in_comments=True was requested.
        if in_comment_region and not in_comments:
            out.append(chunk)
            continue
        new_chunk, n = INCLUDE_LITERAL_RE.subn(
            lambda m: _rewrite_include_match(m), chunk
        )
        count += n
        out.append(new_chunk)
    return "".join(out), count


def transform_comp_include(text: str, *, in_comments: bool = False) -> tuple[str, int]:
    """Rewrite `{% comp_include "X" ... %}` into `{% comp "X" ... / %}`.

    See :func:`transform_include_literal` for the ``in_comments`` behavior.
    """
    count = 0
    out: list[str] = []
    for chunk, in_comment_region in split_outside_comments(text):
        if in_comment_region and not in_comments:
            out.append(chunk)
            continue
        new_chunk, n = COMP_INCLUDE_LITERAL_RE.subn(
            lambda m: _rewrite_comp_include_match(m), chunk
        )
        count += n
        out.append(new_chunk)
    return "".join(out), count


def _rewrite_include_match(m: re.Match[str]) -> str:
    path = m.group(1) or ""
    if not path:
        return m.group(0)
    kwonly = (m.group("kwonly") or "").strip()
    # `{% include "X" with k=v %}` and `{% include "X" only %}` ->
    # `{% comp "X" k=v only / %}`. comp has no `with` keyword — kwargs go
    # directly: `k=v` (no `with` prefix). Also strip a stray trailing `/`
    # so we never produce `' / / %}'` when the caller already wrote one.
    rest = WITH_RE.sub(" ", kwonly).strip()
    bits = [b for b in rest.split() if b and b != "/"]
    joined = " ".join(bits)
    if joined:
        return f'{{% comp "{path}" {joined} / %}}'
    return f'{{% comp "{path}" / %}}'


def _rewrite_comp_include_match(m: re.Match[str]) -> str:
    # Group 1 of COMP_INCLUDE_LITERAL_RE is the path body already de-quoted.
    path = m.group(1) or ""
    if not path:
        return m.group(0)
    kwonly = (m.group("kwonly") or "").strip()
    # Drop any pre-existing `/` self-close marker — we always re-emit one.
    bits = [b for b in kwonly.split() if b and b != "/"]
    joined = " ".join(bits)
    if joined:
        return f'{{% comp "{path}" {joined} / %}}'
    return f'{{% comp "{path}" / %}}'


def transform_file(path: Path, *, in_comments: bool = False) -> tuple[int, int]:
    """Apply all transforms to one file. Returns (lines_changed, sites_changed).

    Pass ``in_comments=True`` to also rewrite inside `{# ... #}` and
    `{% comment %}...{% endcomment %}` blocks (default: skip them).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        print(f"  SKIP {path}: {exc}", file=sys.stderr)
        return 0, 0

    sites = 0
    new_text = text
    new_text, n1 = transform_include_literal(new_text, in_comments=in_comments)
    sites += n1
    new_text, n2 = transform_comp_include(new_text, in_comments=in_comments)
    sites += n2

    if new_text == text:
        return 0, 0

    path.write_text(new_text, encoding="utf-8")
    # Cheap "lines changed" estimate: any line touching a transitioned tag.
    lines_changed = max(n1, n2)
    return lines_changed, sites


def walk(root: Path) -> list[Path]:
    """Recursive file enumeration, skipping vendor / generated directories."""
    out: list[Path] = []
    for p in root.rglob("*.html"):
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        out.append(p)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument(
        "--root",
        type=Path,
        help="Root directory to recursively scan (alternative to listing files).",
    )
    parser.add_argument(
        "--in-comments",
        action="store_true",
        help=(
            "Also rewrite include / comp_include mentions that live INSIDE "
            "`{# ... #}` or `{% comment %}...{% endcomment %}` blocks. Use "
            "this to update stale documentation after a tag is removed."
        ),
    )
    args = parser.parse_args()

    targets: list[Path] = []
    if args.root is not None:
        targets.extend(walk(args.root))
    else:
        for p in args.paths:
            if p.is_dir():
                targets.extend(walk(p))
            elif p.is_file():
                targets.append(p)
            else:
                print(f"WARN: {p} not found", file=sys.stderr)

    if not targets:
        print("No targets.", file=sys.stderr)
        return 1

    total_lines = 0
    total_sites = 0
    files_changed = 0
    for p in sorted(targets):
        lines_changed, sites_changed = transform_file(p, in_comments=args.in_comments)
        if sites_changed:
            files_changed += 1
            total_lines += lines_changed
            total_sites += sites_changed
            print(f"  CHG  {p}  sites={sites_changed}")

    print(f"\n{files_changed} files changed, {total_sites} tag sites migrated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
