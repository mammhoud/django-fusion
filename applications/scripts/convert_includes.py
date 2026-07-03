"""Convert ``{% include "..." %}`` tags to ``{% comp "..." %}`` tags.

This is a pilot tool used to migrate Python codebases from
``{% include %}`` to ``{% comp %}`` for paths that have a thin
component wrapping the same template (see
``comp.registry.register_default_partials``).

Design goals
------------
- Token-based rewrite: walks Django's tokenizer output and uses each
  BLOCK token's ``position`` (a ``(start_offset, end_offset)`` byte
  tuple in Django 4+) to splice in the rewritten form via a cursor
  accumulator. This sidesteps Django's ``Node.source`` - which is a
  ``[origin_name, lineno]`` list and provides only line numbers, not
  byte offsets - and is byte-exact regardless of multi-line tags.
- Safe-by-default: variable-name paths and ``as alias`` includes are
  reported separately and left alone. Re-run with ``--report`` to see
  what was skipped.
- Idempotent: already-converted templates are skipped (no
  ``{% include`` present counter-checks a ``{% comp``).

Usage
-----
The script must be invoked as a file, not as ``-m`` (because the
``applications`` package's ``__init__.py`` does eager CLI imports
that aren't resolvable in this layout)::

    python3 applications/scripts/convert_includes.py assets/templates/partials/
    python3 applications/scripts/convert_includes.py assets/templates/partials/ --report
    python3 applications/scripts/convert_includes.py --dry-run assets/templates/partials/

A ``*.converted.html.bak`` is written next to each rewritten file
unless ``--no-backup`` is passed.

Requires Django >= 4.1 (uses ``Token.position`` byte-offset tuple)
and Django >= 4.2 (`{% include … only %}` tokenisation stability).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

# Configure Django minimally before importing django.template machinery.
# Note: we deliberately do NOT add INSTALLED_APPS — that would force
# the app registry to build and pull unrelated transitive imports. The
# Template lexer only needs TEMPLATES configured.
from django.conf import settings


def _configure_django_minimal() -> None:
    """Boot Django with TEMPLATES-only settings.

    Required because ``django.template.Engine.get_default()`` calls
    ``apps.get_app_configs()`` during backend initialisation, which
    raises ``AppRegistryNotReady`` unless ``django.setup()`` has been
    called. Sites that only need template lexing/install do not need a
    full INSTALLED_APPS list — an empty list is sufficient.
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
                    "OPTIONS": {
                        "context_processors": [],
                    },
                }
            ],
        )
    if not django_apps.ready:
        django.setup()


@dataclass(frozen=True)
class IncludeMatch:
    """A classified ``{% include %}`` token-match from a single template."""

    path: str  # empty string when path is a runtime variable
    kwargs_str: str  # raw kwargs text after ``with ``; empty when no kwargs
    only: bool
    skip_reason: str | None  # "variable-path" | "as-alias" | None
    line: int = 0  # 1-based source line; 0 when unparsable/unknown


# Matches the interior of an include tag. Captures:
#   1: quoted path OR raw variable name (no quotes)
#   2: kwargs-after-with (may be empty; bounded by the next ``only``/``as``/EOL)
#   3: optional leading ``only`` (BEFORE with)
#   4: optional trailing ``only`` (AFTER with / standalone)
#   5: optional ``as alias`` suffix
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


def _parse_include_contents(contents: str) -> IncludeMatch:
    """Classify the body of a ``{% include ... %}`` TOKEN contents."""
    m = _INCLUDE_RE.match(contents.strip())
    if not m:
        return IncludeMatch(
            path="", kwargs_str="", only=False, skip_reason="unparsable"
        )
    raw_path = m.group("path")
    if raw_path.startswith(("\"", "'")):
        path = raw_path[1:-1]
    else:
        return IncludeMatch(
            path="", kwargs_str="", only=False, skip_reason="variable-path"
        )
    is_only = bool(m.group("only_before") or m.group("only_after"))
    if m.group("as"):
        return IncludeMatch(
            path=path,
            kwargs_str=(m.group("with") or "").strip(),
            only=is_only,
            skip_reason="as-alias",
        )
    return IncludeMatch(
        path=path,
        kwargs_str=(m.group("with") or "").strip(),
        only=is_only,
        skip_reason=None,
    )


def _build_comp_call(match: IncludeMatch) -> str:
    """Build the ``{% comp "path" ... / %}`` string from a classified match."""
    bits = [f'"{match.path}"']
    if match.only:
        bits.append("only")
    if match.kwargs_str:
        bits.append(match.kwargs_str)
    return "{% comp " + " ".join(bits) + " /%}"


def rewrite_template(
    raw: str,
) -> tuple[str, list[IncludeMatch], list[tuple[str, str, int]]]:
    """Rewrite ``raw`` by tokenizing and splicing include tokens.

    Uses ``django.template.base.Lexer`` to tokenize the source (not
    ``Engine.get_default().lex()``, which is brittle in narrow
    configurations), then walks each BLOCK include token and splices
    the rewritten ``{% comp ... / %}`` form using the cursor-
    accumulator technique. ``tok.position`` is a ``(start_offset,
    end_offset)`` byte tuple, which makes the splice byte-exact for
    multi-line tags and unusual whitespace patterns.

    Line numbers for ``--report`` are computed from the byte position
    via newline-counting in ``raw`` because Lexer-produced Token
    objects do not expose the ``.source`` attribute that the older
    Engine-lex path left on its tokens.

    Returns
    -------
    tuple[str, list[IncludeMatch], list[tuple[str, str, int]]]
        New text, list of converted matches (for reporting),
        list of ``(skipped_contents, reason, line)`` triples.
    """
    from django.template.base import Lexer, TokenType  # noqa: PLC0415

    # ``Engine.lex`` exists in modern Django but is brittle in narrow
    # configurations (and absent in some shim engines); ``Lexer`` is
    # stable across all Django 4.x and does not need an ``Engine``
    # instance. ``Lexer(raw).tokenize()`` returns the same ``Token``
    # stream with ``.position`` byte offsets and ``.token_type``
    # membership on ``TokenType``.
    tokens = Lexer(raw).tokenize()

    converted: list[IncludeMatch] = []
    skipped: list[tuple[str, str, int]] = []
    new_parts: list[str] = []
    cursor = 0
    lexer_cursor = 0  # tracks sequential byte position for Django 5.2+ fallback

    for tok in tokens:
        # Reconstruct byte position for Django 5.2+ where Lexer omits
        # ``.position``.  Search for the token contents starting from
        # ``lexer_cursor`` (the end of the previous token) to ensure
        # sequential safety, then expand outward to ``{`` / ``}``
        # delimiters for non-TEXT tokens.
        pos = tok.position
        if pos is None:
            content_idx = raw.find(tok.contents, lexer_cursor)
            if content_idx >= 0:
                if tok.token_type == TokenType.TEXT:
                    pos = (content_idx, content_idx + len(tok.contents))
                else:
                    start = raw.rfind("{", lexer_cursor, content_idx)
                    end = raw.find("}", content_idx + len(tok.contents))
                    if start >= 0 and end >= 0:
                        pos = (start, end + 1)

        # Advance the sequential cursor for the next token.
        if pos is not None:
            lexer_cursor = pos[1]

        if tok.token_type != TokenType.BLOCK:
            continue
        c = tok.contents.strip()
        if not c.startswith("include "):
            continue

        match = _parse_include_contents(c)
        # Use the byte position to derive the 1-based line number by
        # counting newlines in ``raw`` up to the token's start offset.
        # ``Lexer`` may yield tokens whose ``position`` is ``None``
        # (e.g. comment-only fragments inside the leading text or
        # buffer placeholders); compute a fallback offset from the
        # literal token contents via ``str.find`` so we never feed
        # ``None`` into ``raw[:None]``.
        if pos is not None:
            pos_offset: int = pos[0]
        else:
            found = raw.find(tok.contents, cursor)
            pos_offset = found if found >= 0 else 0
        line = raw[:pos_offset].count("\n") + 1

        if match.skip_reason:
            skipped.append((c, match.skip_reason, line))
            continue

        if pos is None:
            # Cannot splice safely without byte offsets. Skip this
            # include token and let the user fix the source manually.
            skipped.append((c, "no-position", line))
            continue
        start, end = pos
        # Carry the source line through IncludeMatch so --report can show
        # it for both converted and skipped entries. IncludeMatch is
        # frozen + slotted; recreate rather than mutate.
        match = IncludeMatch(
            path=match.path,
            kwargs_str=match.kwargs_str,
            only=match.only,
            skip_reason=match.skip_reason,
            line=line,
        )
        new_parts.append(raw[cursor:start])
        new_parts.append(_build_comp_call(match))
        cursor = end
        converted.append(match)

    new_parts.append(raw[cursor:])
    return "".join(new_parts), converted, skipped


def iter_html_files(roots: Iterable[str]) -> Iterable[Path]:
    for root_str in roots:
        root = Path(root_str)
        if root.is_file() and root.suffix == ".html":
            yield root
            continue
        if root.is_dir():
            yield from sorted(root.rglob("*.html"))


def _already_converted(raw: str) -> bool:
    return "{% comp " in raw and "{% include " not in raw


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("roots", nargs="+", help="Directories or files to migrate.")
    parser.add_argument("--dry-run", action="store_true", help="Print would-be diffs, do not write.")
    parser.add_argument("--no-backup", action="store_true", help="Skip *.converted.html.bak backup write.")
    parser.add_argument(
        "--report",
        action="store_true",
        help="After run, list converted AND skipped include tokens (variable-path / as-alias / unparsable).",
    )
    args = parser.parse_args(argv)

    _configure_django_minimal()

    files_total = 0
    converted_total = 0
    skipped_total = 0
    converted_log: list[tuple[Path, str, int]] = []
    skipped_log: list[tuple[Path, str, str, int]] = []

    for path in iter_html_files(args.roots):
        files_total += 1
        raw = path.read_text(encoding="utf-8")
        if "{% include " not in raw:
            continue
        if _already_converted(raw):
            continue

        new_raw, converted, skipped = rewrite_template(raw)
        if not converted:
            continue

        if args.dry_run:
            print(f"[dry-run] {path}: would convert {len(converted)} include(s)")

        if not args.dry_run:
            if not args.no_backup:
                backup = path.with_suffix(path.suffix + ".converted.html.bak")
                backup.write_text(raw, encoding="utf-8")
            path.write_text(new_raw, encoding="utf-8")

        converted_total += len(converted)
        skipped_total += len(skipped)
        if args.report:
            for m in converted:
                converted_log.append((path, m.path, m.line))
            for contents, reason, line in skipped:
                skipped_log.append((path, contents, reason, line))

    print(f"Files scanned:      {files_total}")
    print(f"Includes converted: {converted_total}")
    print(f"Includes skipped:   {skipped_total}  (run with --report to list)")

    if args.report:
        if converted_log:
            print("\nConverted:")
            for p, pth, ln in converted_log:
                print(f"  + {p}:{ln}  {pth}")
        if skipped_log:
            print("\nSkipped (review manually):")
            for p, contents, reason, ln in skipped_log:
                print(f"  ! {p}:{ln}  [{reason}]  {contents}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
