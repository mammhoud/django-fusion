"""CI script: validate every ``[pkg-extras]`` reference in Markdown install
commands under ``libs/**/docs/`` against the corresponding lib's
``pyproject.toml`` ``[project.optional-dependencies]``.

The script extracts every install command of the form::

    uv add "pkg[a,b,c]"            # and --dev variants
    uv add "pkg[a,b,c]" --dev
    uv pip install "pkg[a,b,c]"
    pip install "pkg[a,b,c]"

then resolves each ``pkg`` to ``libs/<pkg>/pyproject.toml`` and
checks every extra is a declared key in that file's
``[project.optional-dependencies]`` table.

Why this exists
---------------

Earlier in this codebase, ``legacy-ceptor-ai/README.md`` listed extras
``openai``, ``anthropic``, and ``faker`` that did **not exist** in the
corresponding ``pyproject.toml``. This script — paired with the GH Actions
workflow at ``.github/workflows/check-extras.yml`` — ensures that class of
doc drift can't ship on a PR.

Notes
-----

* Library package names use hyphens (``ceptor-ai``, ``django-fusion``) per PEP
  621;  the dict under ``libs`` mirrors that. So the mapping is
  literally ``libs/{pkg}/pyproject.toml``.
* ``pip install`` is treated leniently: anything after the install command up to
  the closing quote of the first quoted token is considered irrelevant for
  extras validation.
* Lines inside fenced code blocks (``\`\`\` … \`\`\``) or indented code blocks
  are ignored — they may legitimately demo extras from other ecosystems.
* HTTP/SSH URLs (``uv add git+https://…``) and pure version specs
  (``pip install foo>=2.0`` without extras) are inert: we only validate when
  an extras list ``[…]`` is present and the package name points at a libs dir.

Exit codes
----------

* ``0`` — every extras reference resolves.
* ``1`` — at least one extra missing or unparseable, or a fatal scan error.
* ``2`` — Python interpreter is older than 3.11 (``tomllib`` unavailable).

Pair with ``.github/workflows/check-extras.yml`` for the CI gate.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# tomllib was added to the Python standard library in 3.11. Earlier versions
# need the third-party ``tomli`` package as a backport. Per project convention
# (no try/except around imports), we fail fast with a clear message instead.
if sys.version_info < (3, 11):
    sys.stderr.write(
        f"error: this script requires Python 3.11+ (for stdlib tomllib). "
        f"Found: {sys.version}. "
        f"Install a 3.11+ interpreter or pin python-version: '3.11' in your workflow.\n"
    )
    sys.exit(2)

import tomllib  # noqa: E402  (deliberately after the version gate above)

# This script lives at application/scripts/check_extras_in_docs.py.
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCOPE = REPO_ROOT / "libs"

# Install commands we validate against. Captures: ``cmd`` (uv|pip), optional
# `uv pip` qualifier, ``sub`` (add|install), opening+closing quote pair,
# package name, and the comma-separated ``extras`` list inside ``[…]``.
INSTALL_RE = re.compile(
    r'(?:^|[^a-zA-Z])(?P<cmd>uv|pip)\b'
    r'(?:\s+pip)?'
    r'\s+(?P<sub>add|install)\b'
    r'\s+'
    r'(?P<quot>["\'])'
    r'(?P<pkg>[a-zA-Z0-9][\w\.\-]*)'
    r'(?:\[(?P<extras>[^\]]+)\])?'
    r'(?P=quot)'
)

FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def _strip_code_regions(line: str) -> str:
    """Replace inline-code spans with whitespace (preserve positions)."""
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line)


def _resolve_pkg_pyproject(pkg: str, libs_dir: Path) -> Path | None:
    """Return the libs subdir pyproject.toml for *pkg* (using its literal name
    as the directory name; PEP 621: package name == directory name in this project).
    Returns ``None`` if no candidate exists under libs.
    """
    candidate = libs_dir / pkg / "pyproject.toml"
    return candidate if candidate.is_file() else None


def _declared_extras(pyproject: Path) -> set[str]:
    """Read the pyproject.toml and return the set of extras declared under
    ``[project.optional-dependencies]`` (keys). Missing or empty table → empty set.
    """
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    optional = data.get("project", {}).get("optional-dependencies", {})
    if not isinstance(optional, dict):
        return set()
    return {str(k) for k in optional.keys()}


def _iter_install_lines(text: str):
    """Yield ``(lineno, original_line, scan_line)`` tuples for every non-fenced
    line in ``text`` (skipping code fences).
    """
    in_fence = False
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield lineno, raw, _strip_code_regions(raw)


def _scan_doc_file(file_path: Path, libs_dir: Path, errors: list[tuple[Path, int, str]]):
    """Scan one README; append (file:line, summary_message) for every
    invalid (pkg, extras) reference.
    """
    text = file_path.read_text(encoding="utf-8")
    for lineno, raw, scan_line in _iter_install_lines(text):
        for m in INSTALL_RE.finditer(scan_line):
            pkg = m.group("pkg")
            extras = m.group("extras")
            if not extras:
                # No extras in this line — out of scope for this script.
                continue
            pyproject = _resolve_pkg_pyproject(pkg, libs_dir)
            if pyproject is None:
                # Package isn't in libs/ → not a libs dependency; skip silently.
                continue
            declared = _declared_extras(pyproject)
            extras_list = [e.strip() for e in extras.split(",") if e.strip()]
            unknown = [e for e in extras_list if e not in declared]
            if unknown:
                rel = file_path.relative_to(REPO_ROOT).as_posix()
                summary = (
                    f'  BROKEN  {rel}:{lineno}  pkg="{pkg}" '
                    f'extras=[{", ".join(extras_list)}] '
                    f'unknown=[{", ".join(unknown)}]  '
                    f'(declared: {{{", ".join(sorted(declared)) or "(none)"}}})'
                )
                errors.append((file_path, lineno, summary))


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--scope",
        type=Path,
        default=DEFAULT_SCOPE,
        help=f"Directory to scan for Markdown files (default: {DEFAULT_SCOPE.relative_to(REPO_ROOT)}).",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    scope = args.scope.resolve()
    if not scope.is_dir():
        print(f"error: scope {scope} is not a directory", file=sys.stderr)
        return 2

    files = sorted(scope.rglob("**/docs/**/*.md"))
    if not files:
        print(f"(no Markdown files under {scope.relative_to(REPO_ROOT)}/**/docs/)", file=sys.stderr)
        return 0

    errors: list[tuple[Path, int, str]] = []
    print(f"scanning {len(files)} Markdown file(s) under {scope.relative_to(REPO_ROOT)}/**/docs/")

    for f in files:
        _scan_doc_file(f, scope, errors)

    print(f"extras drift: {len(errors)} broken reference(s)")
    for _, _, summary in errors:
        print(summary)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
