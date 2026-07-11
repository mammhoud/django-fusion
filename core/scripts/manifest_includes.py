"""manifest_includes.py — read-only audit of every ``{% include %}`` tag.

Goal
----
Tell the operator, BEFORE running :mod:`applications.scripts.convert_includes`,
how many include directives in the tree are safe to auto-convert vs which
need manual review.

Walks the conventional template roots across the monorepo, tokenises each
``.html`` file with :class:`django.template.base.Lexer` (no Engine required,
no template backend), and classifies every ``{% include %}`` token into
one of the four buckets below.

Classification
--------------
``literal``
    Path is a quoted string (``"foo.html"`` / ``'foo.html'``) OR an
    unquoted token that looks like a static file path
    (``partials/foo.html``, ``_buttons/nav.html``). SAFE to
    auto-convert.

``variable``
    Path is unquoted and not path-shaped — Django's lexer stripped it
    down to a FilterExpression resolved at render time
    (``{% include foo %}``, ``{% include item.template %}``). NOT safe
    to auto-convert because the path is data, not source.

``commented``
    Token lives inside a ``{# ... #}`` Django comment span. Tracked
    but EXCLUDED from the active-include total because the directive
    doesn't run.

``aliased``
    *Cross-cutting flag*, NOT a bucket. Set when the include uses
    ``as <name>``. Because ``as`` rebinds the rendered block as a
    context variable in the OUTER template, converting
    ``{% include "x" as v %}`` to ``{% comp "x" / %}`` changes the
    outer-scope semantics, so aliased includes (literal OR variable)
    need manual review even when the path is literal.

Usage
-----
::

    python3 applications/scripts/manifest_includes.py
    python3 applications/scripts/manifest_includes.py applications/assets/templates/
    python3 applications/scripts/manifest_includes.py --json | jq '.buckets'

Default roots (without arguments) walk the conventional template trees
across all three sites plus the shared asset tree::

    applications/assets/templates/
    applications/<site>/templates/        (one per site in applications/)
    applications/<site>/assets/templates/ (one per site that has one)
    applications/<site>/www/**/templates/ (Django-app templates)

Requires Django >= 4.1 (uses ``TokenType``, ``Lexer.tokenize``).
The script will lazily ``settings.configure`` a TEMPLATES-only Django
env if one isn't already present (same shape as ``convert_includes.py``).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from django.conf import settings

# ---------------------------------------------------------------------------
# Django bootstrap (TEMPLATES-only, same shape as convert_includes.py).
# ---------------------------------------------------------------------------


def _configure_django_minimal() -> None:
    """Boot Django with TEMPLATES-only settings.

    Required because ``Lexer`` lazily constructs a ``Parser`` that pulls
    from ``Engine.get_default()``, which in turn calls
    ``apps.get_app_configs()`` and raises ``AppRegistryNotReady`` unless
    ``django.setup()`` has been called. Sites that only need template
    lexing/install do not need a full INSTALLED_APPS list.
    """
    import django  # noqa: PLC0415
    from django.apps import apps as django_apps  # noqa: PLC0415

    if not settings.configured:
        settings.configure(
            DEBUG=False,
            INSTALLED_APPS=[],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": False,
                    "OPTIONS": {"context_processors": []},
                }
            ],
        )
    if not django_apps.ready:
        django.setup()


# ---------------------------------------------------------------------------
# Classification — mirrors convert_includes.py's _INCLUDE_RE so the two
# scripts agree on what counts as "literal" + "with" + "only".
# ---------------------------------------------------------------------------


# Matches the interior of a {% include .. %} tag block contents.
# Captures (in order): path, only-before, with-kwargs, only-after,
# as-alias. Bounded by ``\s*$`` to keep the entire tag body in scope.
_INCLUDE_RE = re.compile(
    r"""
    \s*include\s+(?P<path>"[^"]+"|'[^']+'|[^\s]+)
    (?P<only_before>\s+only)?
    (?:\s+with\s+(?P<with>.*?))?
    (?P<only_after>\s+only)?
    (?:\s+as\s+(?P<as>\w+))?
    \s*$
    """,
    re.VERBOSE,
)

# Heuristic for "looks like a static file path" on unquoted tokens.
# Matches: foo.html, partials/foo.html, _partials/sub/foo-bar.html
# Skips:   foo (no extension), item.template (.template is not .html),
#          obj.method (no extension).
_STATIC_PATH_RE = re.compile(r"^[\w][\w./-]*\.html?$")

# Recognise an ``{% include … %}`` directive INSIDE a Django comment
# span (``{# … #}``). Strict-shape match, NOT a substring: this
# excludes documentation comments like ``{# see the include docs #}``
# from being mistaken for commented-out directives.
_INCLUDE_COMMENT_RE = re.compile(r"\s*\{%\s*include\b")


@dataclass(frozen=True)
class IncludeRecord:
    """One ``{% include %}`` token, classified."""

    bucket: str  # "literal" | "variable" | "commented"
    path: str  # quoted-stripped path for literal; raw token for variable
    aliased: bool = False
    has_with: bool = False
    has_only: bool = False
    line: int = 0  # 1-based; 0 when unparsable

    @property
    def is_safe_to_auto_convert(self) -> bool:
        """True iff bucket == literal AND not aliased.

        Converting ``{% include "x" as v %}`` -> ``{% comp "x" / %}``
        drops the alias binding in the outer template, which is a silent
        behaviour change. Warrants manual review.
        """
        return self.bucket == "literal" and not self.aliased


def _classify_contents(contents: str) -> tuple[str, str, bool, bool, bool]:
    """Classify a BLOCK token's contents.

    Returns
    -------
    tuple[bucket, path, has_with, has_only, aliased]
        ``bucket`` is one of "literal" / "variable". "commented" is set
        by the caller because it comes from token_type, not contents.
        ``path`` is the quoted-stripped path for literal entries, or the
        raw first-token for variable entries (so we can show it in the
        report).
    """
    m = _INCLUDE_RE.match(contents.strip())
    if not m:
        return ("variable", contents, False, False, False)

    raw_path = m.group("path")
    only_before = bool(m.group("only_before"))
    only_after = bool(m.group("only_after"))
    has_with = bool(m.group("with"))
    has_only = only_before or only_after
    aliased = bool(m.group("as"))

    if raw_path.startswith(("\"", "'")):
        return ("literal", raw_path[1:-1], has_with, has_only, aliased)

    # Unquoted. If it's path-shaped (e.g. ``partials/foo.html``), Django
    # treats it as a string literal at parse time, so classify as
    # literal. Otherwise it's a FilterExpression — variable.
    if _STATIC_PATH_RE.match(raw_path):
        return ("literal", raw_path, has_with, has_only, aliased)
    return ("variable", raw_path, has_with, has_only, aliased)


# ---------------------------------------------------------------------------
# Tokenisation + walking.
# ---------------------------------------------------------------------------


def _iter_include_records(
    raw: str,
) -> tuple[list[IncludeRecord], list[IncludeRecord]]:
    """Tokenise ``raw`` and return (active_records, commented_records).

    The split is by token_type: TokenType.COMMENT spans enclose
    directives that should NOT be counted as active includes.
    """
    from django.template.base import Lexer, TokenType  # noqa: PLC0415

    active: list[IncludeRecord] = []
    commented: list[IncludeRecord] = []

    comment_depth = 0
    for tok in Lexer(raw).tokenize():
        # ``{# ... #}`` is a Token with token_type == COMMENT (Django
        # 4.x). We never open/close ``{% comment %}`` blocks here —
        # those come through as BLOCK tokens containing
        # ``comment ... endcomment`` which we recognise by contents.
        c = tok.contents

        # Handle the `{% comment %} ... {% endcomment %}` shape, which
        # the Lexer returns as two BLOCK tokens (one for the opening,
        # one for ``endcomment``); any BLOCK token with contents
        # starting with ``comment `` (and not ``endcomment``) opens a
        # comment span that closes when we see contents starting with
        # ``endcomment``.
        stripped = c.strip()
        if stripped.startswith("comment ") or stripped == "comment":
            comment_depth += 1
            continue
        if stripped == "endcomment":
            comment_depth = max(0, comment_depth - 1)
            continue
        if comment_depth > 0:
            continue

        # Single-line {# ... #} comments come through as COMMENT tokens.
        # Only treat them as ``commented include directives`` when the
        # contents match the directive shape exactly -- otherwise we
        # would inflate the count with documentation comments like
        # ``{# see include docs #}``.
        if tok.token_type == TokenType.COMMENT:
            if _INCLUDE_COMMENT_RE.match(c):
                commented.append(
                    IncludeRecord(
                        bucket="commented",
                        path=c.strip(),
                        line=_line_for(raw, tok),
                    )
                )
            continue

        if tok.token_type != TokenType.BLOCK:
            continue
        if not stripped.startswith("include"):
            continue
        if not stripped.startswith("include ") and stripped != "include":
            # Defensive: ``includefoo`` should not match.
            continue

        bucket, path, has_with, has_only, aliased = _classify_contents(c)

        # Derive line from the token's byte position (Django 4+ fills
        # ``position`` with ``(start_offset, end_offset)``; fall back to
        # ``raw.find(contents)`` if missing).
        line = _line_for(raw, tok)
        active.append(
            IncludeRecord(
                bucket=bucket,
                path=path,
                aliased=aliased,
                has_with=has_with,
                has_only=has_only,
                line=line,
            )
        )
    return active, commented


def _line_for(raw: str, tok) -> int:
    """Best-effort 1-based line number for a token."""
    pos = getattr(tok, "position", None)
    if pos is None:
        # Lexer-produced tokens don't always expose ``position`` for
        # comment-only fragments; fall back to ``raw.find`` on contents.
        found = raw.find(tok.contents)
        offset = found if found >= 0 else 0
    else:
        offset = pos[0]
    return raw[:offset].count("\n") + 1


# ---------------------------------------------------------------------------
# Tree walking.
# ---------------------------------------------------------------------------


# Default roots to audit. We pick the conventional template trees used
# by this monorepo: shared assets + per-site templates + per-site assets
# + per-site Django-app templates (``www/**/templates``).
_DEFAULT_ROOT_GLOBS: tuple[str, ...] = (
    "applications/assets/templates/",
    "applications/*/templates/",
    "applications/*/assets/templates/",
    "applications/*/www/**/templates/",
)

# Directories that should never be walked even if they live under a
# template root. Avoids pulling in build output, vendored assets, and
# Python bytecode caches that may sit next to (or inside) a templates
# tree on individual sites.
_SKIP_DIRS: frozenset[str] = frozenset(
    {
        "__pycache__",
        "node_modules",
        ".git",
        "dist",
        "build",
        ".venv",
        "venv",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "static",
    }
)


def _resolve_root(root_str: str, project_root: Path) -> Path:
    p = Path(root_str)
    if not p.is_absolute():
        p = project_root / p
    return p


def _default_roots(project_root: Path) -> list[Path]:
    roots: list[Path] = []
    for pattern in _DEFAULT_ROOT_GLOBS:
        for hit in sorted(project_root.glob(pattern)):
            if hit.is_dir():
                roots.append(hit)
    return roots


def iter_html_files(roots: Iterable[Path]) -> Iterable[Path]:
    for root in roots:
        if root.is_file() and root.suffix == ".html":
            yield root
            continue
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.html")):
            # path is ``root / whatever / foo.html``; ``parts[:-1]`` is
            # the directory chain between ``root`` and the file. Skip
            # any chain that touches a known-noise directory.
            try:
                rel_parts = path.relative_to(root).parts[:-1]
            except ValueError:
                rel_parts = ()
            if any(part in _SKIP_DIRS for part in rel_parts):
                continue
            yield path


# ---------------------------------------------------------------------------
# Aggregation + reporting.
# ---------------------------------------------------------------------------


@dataclass
class Manifest:
    files_scanned: int = 0
    files_with_includes: int = 0
    total_active: int = 0
    total_commented: int = 0

    bucket_counts: Counter = field(default_factory=Counter)
    # bucket -> Counter(path -> occurrences)
    paths_by_bucket: dict[str, Counter] = field(
        default_factory=lambda: defaultdict(Counter)
    )
    # (bucket, aliased) -> count  -- lets us split "literal + aliased" out
    aliased_within_bucket: dict[tuple[str, bool], int] = field(
        default_factory=dict
    )
    # bucket -> counter of distinct paths that appear with `with` / `only`
    flags_within_bucket: dict[str, Counter] = field(
        default_factory=lambda: defaultdict(Counter)
    )

    example_records: dict[str, list[IncludeRecord]] = field(
        default_factory=lambda: defaultdict(list)
    )


def build_manifest(files: Iterable[Path]) -> Manifest:
    m = Manifest()
    for path in files:
        m.files_scanned += 1
        raw = path.read_text(encoding="utf-8", errors="replace")
        active, commented = _iter_include_records(raw)
        if not active and not commented:
            continue
        m.files_with_includes += 1
        m.total_active += len(active)
        m.total_commented += len(commented)
        for rec in commented:
            m.bucket_counts["commented"] += 1
            if len(m.example_records["commented"]) < 5:
                m.example_records["commented"].append(rec)
        for rec in active:
            m.bucket_counts[rec.bucket] += 1
            m.paths_by_bucket[rec.bucket][rec.path] += 1
            key = (rec.bucket, rec.aliased)
            m.aliased_within_bucket[key] = m.aliased_within_bucket.get(key, 0) + 1
            # Flag bit-set: include directives can carry BOTH ``with``
            # and ``only`` simultaneously (e.g.
            # ``{% include "x" with f=1 only %}``); encode each flag
            # separately so the per-bucket counts are not mutually
            # exclusive.
            parts: list[str] = []
            if rec.has_with:
                parts.append("with")
            if rec.has_only:
                parts.append("only")
            flag = ",".join(parts) if parts else "plain"
            m.flags_within_bucket[rec.bucket][flag] += 1
            if len(m.example_records[rec.bucket]) < 8:
                m.example_records[rec.bucket].append(rec)
    return m


def render_text(manifest: Manifest, roots: list[Path]) -> str:
    out: list[str] = []
    bar = "=" * 68
    half = "-" * 68
    out.append(bar)
    out.append(" INCLUDE TAG MANIFEST ".center(68, "="))
    out.append(bar)
    out.append("")
    out.append(f"  Roots audited:        {_fmt_roots(roots)}")
    out.append(f"  Files scanned:        {manifest.files_scanned}")
    out.append(f"  Files with includes:  {manifest.files_with_includes}")
    out.append(f"  Active include tags:  {manifest.total_active}")
    out.append(
        f"  Commented includes:   {manifest.total_commented}"
        "  (inside {# ... #} or {% comment %} ... {% endcomment %}; excluded)"
    )
    out.append("")

    for bucket in ("literal", "variable"):
        out.append(half)
        out.append(f" {bucket.upper()} ".center(68, "-"))
        out.append(half)
        count = manifest.bucket_counts.get(bucket, 0)
        out.append(f"  count:               {count}")
        if count == 0:
            out.append("")
            continue

        paths = manifest.paths_by_bucket[bucket]
        out.append(f"  distinct paths:      {len(paths)}")

        # Aliased breakdown within this bucket.
        aliased_n = manifest.aliased_within_bucket.get((bucket, True), 0)
        not_aliased_n = manifest.aliased_within_bucket.get((bucket, False), 0)
        out.append("")
        out.append(f"  as-alias:            {aliased_n}   (manual review needed)")
        out.append(f"  no as-alias:         {not_aliased_n}")

        # Flag breakdown within this bucket.
        flags = manifest.flags_within_bucket.get(bucket, Counter())
        out.append("")
        out.append("  include-flag breakdown:")
        for flag in ("plain", "only", "with"):
            out.append(f"    {flag:<6} {flags.get(flag, 0)}")

        # Top paths by occurrence.
        if paths:
            out.append("")
            out.append(f"  top paths (count, up to 12 shown):")
            for path, n in paths.most_common(12):
                out.append(f"    {n:>4}  {path}")

        # Examples.
        examples = manifest.example_records.get(bucket, [])
        if examples:
            out.append("")
            out.append("  examples:")
            for rec in examples:
                tag = _render_tag(rec)
                out.append(f"    {tag}")
                if rec.line:
                    out.append(f"           (line {rec.line})")

        out.append("")

    if manifest.total_commented:
        out.append(half)
        out.append(" COMMENTED ".center(68, "-"))
        out.append(half)
        out.append(f"  count:               {manifest.total_commented}")
        examples = manifest.example_records.get("commented", [])
        if examples:
            out.append("  examples (text shown verbatim):")
            for rec in examples:
                out.append(f"    {{# {rec.path} #}}")
        out.append("")

    out.append(half)
    out.append(" SUMMARY ".center(68, "-"))
    out.append(half)
    literal = manifest.bucket_counts.get("literal", 0)
    variable = manifest.bucket_counts.get("variable", 0)
    commented = manifest.bucket_counts.get("commented", 0)
    literal_aliased = manifest.aliased_within_bucket.get(("literal", True), 0)
    literal_safe = manifest.aliased_within_bucket.get(("literal", False), 0)
    out.append(f"  Literal, no `as` (auto-convert safe):   {literal_safe}")
    out.append(f"  Literal + `as <name>` (review):         {literal_aliased}")
    out.append(f"  Variable (do NOT auto-convert):         {variable}")
    out.append(f"  Already commented (excluded):           {commented}")
    total_active = manifest.total_active or 1
    pct_safe = literal_safe * 100.0 / total_active
    out.append("")
    out.append(f"  -> {pct_safe:.1f}% of active includes are safe to auto-convert.")
    out.append("")
    return "\n".join(out)


def _fmt_roots(roots: list[Path]) -> str:
    if not roots:
        return "(none resolved)"
    if len(roots) == 1:
        return str(roots[0])
    return f"{len(roots)} dirs (use --show-roots to list)"


def _render_tag(rec: IncludeRecord) -> str:
    """Render a representative ``{% include ... %}`` tag for a record."""
    if rec.bucket == "commented":
        return f"{{# ... #}}"
    head = "{% include"
    if rec.path and (rec.path.startswith("'") or rec.path.startswith('"')):
        head += f" {rec.path}"
    elif rec.path:
        head += f" {rec.path}"
    extras: list[str] = []
    if rec.has_with:
        extras.append("with ...")
    if rec.has_only:
        extras.append("only")
    if rec.aliased:
        extras.append("as <name>")
    if extras:
        head += " " + " ".join(extras)
    return head + " %}"


def render_json(manifest: Manifest) -> str:
    payload = {
        "totals": {
            "files_scanned": manifest.files_scanned,
            "files_with_includes": manifest.files_with_includes,
            "active_include_tags": manifest.total_active,
            "commented_include_tags": manifest.total_commented,
        },
        "buckets": {
            bucket: {
                "count": manifest.bucket_counts.get(bucket, 0),
                "distinct_paths": len(manifest.paths_by_bucket[bucket]),
                "aliased": manifest.aliased_within_bucket.get(
                    (bucket, True), 0
                ),
                "not_aliased": manifest.aliased_within_bucket.get(
                    (bucket, False), 0
                ),
                "flags": dict(manifest.flags_within_bucket.get(bucket, {})),
                "top_paths": dict(
                    manifest.paths_by_bucket[bucket].most_common(20)
                ),
            }
            for bucket in ("literal", "variable", "commented")
        },
        "safe_to_auto_convert": manifest.aliased_within_bucket.get(
            ("literal", False), 0
        ),
    }
    return json.dumps(payload, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    project_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(
        prog="manifest_includes.py",
        description=__doc__.splitlines()[1],
    )
    parser.add_argument(
        "roots",
        nargs="*",
        help=(
            "Directories or files to audit. Defaults to the conventional "
            "template trees across the monorepo "
            "(applications/assets/templates/, applications/<site>/templates/, "
            "applications/<site>/assets/templates/, applications/<site>/www/**/templates/)."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of the text table (pipe-friendly).",
    )
    parser.add_argument(
        "--show-roots",
        action="store_true",
        help="Print the resolved roots before the report.",
    )
    args = parser.parse_args(argv)

    _configure_django_minimal()

    if args.roots:
        roots = [_resolve_root(r, project_root) for r in args.roots]
    else:
        roots = _default_roots(project_root)

    if args.show_roots:
        print("Resolved roots:", file=sys.stderr)
        for r in roots:
            print(f"  {r}", file=sys.stderr)

    files = list(iter_html_files(roots))
    manifest = build_manifest(files)

    if args.json:
        print(render_json(manifest))
    else:
        print(render_text(manifest, roots))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
