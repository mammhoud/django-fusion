#!/usr/bin/env python3
"""CI + pre-commit checker: scan git-tracked source files for known typos and
dead-code patterns to prevent regressions.

Patterns checked
----------------

**Typos** (case-insensitive, word-bounded):
    fuson         -> fusion
    fussion       -> fusion
    fuction       -> function
    recieved      -> received
    seperate      -> separate
    occured       -> occurred
    definately    -> definitely
    sucess        -> success
    thier         -> their
    accomodate    -> accommodate
    dependant     -> dependent
    existant      -> existent
    maintainence  -> maintenance
    neccessary    -> necessary
    noticable     -> noticeable
    priviledge    -> privilege
    publically    -> publicly
    untill        -> until

**Dead code** (case-insensitive):
    TODO:\\s*remove
    FIXME:\\s*delete

Allowlist
---------

Any line containing the substring ``lint-disable-line`` is ignored.
Works across Python (# lint-disable-line), JS/TS (// lint-disable-line),
HTML (<!-- lint-disable-line -->), and SCSS (// lint-disable-line).

Scoping
-------

Only git-tracked files are scanned. The script enumerates files via
``git ls-files`` (which already respects .gitignore), then filters by:

* Included extensions: .py, .ts, .tsx, .js, .jsx, .html, .scss, .md,
  .yaml, .yml, .sh
* Excluded paths (even if tracked): libs/django-fusion/*, libs/ceptor-ai/*,
  uv.lock, package-lock.json, **/dump-data.json, **/fixtures/**,
  **/test-data/**

Usage
-----

::

    python3 application/scripts/dev/check_typos_and_deadcode.py

Exit codes:
    0 - clean, no matches found
    1 - one or more matches found
    2 - fatal error (git not available, etc.)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# ── Patterns ────────────────────────────────────────────────────────────────

# (regex_pattern, error_kind, suggestion)
# All typo patterns are case-insensitive, anchored on the LEFT with a word
# boundary (``\b``). There is NO trailing boundary so we also catch typos
# used as identifiers (``recieved_data``, ``fuson_engine``) and not just
# standalone words. This is the right trade-off for code: rare longer words
# that happen to start with a typo prefix (e.g. ``fusonage``) are acceptable
# false positives vs. missing every identifier-style typo.
TYPO_PATTERNS: list[tuple[str, str, str]] = [
    (r"\bfuson",         "TYPO",  "fusion"),
    (r"\bfussion",       "TYPO",  "fusion"),
    (r"\bfuction",       "TYPO",  "function"),
    (r"\brecieved",      "TYPO",  "received"),
    (r"\bseperate",      "TYPO",  "separate"),
    (r"\boccured",       "TYPO",  "occurred"),
    (r"\bdefinately",    "TYPO",  "definitely"),
    (r"\bsucess",        "TYPO",  "success"),
    (r"\bthier",         "TYPO",  "their"),
    (r"\baccomodate",    "TYPO",  "accommodate"),
    (r"\bdependant",     "TYPO",  "dependent"),
    (r"\bexistant",      "TYPO",  "existent"),
    (r"\bmaintainence",  "TYPO",  "maintenance"),
    (r"\bneccessary",    "TYPO",  "necessary"),
    (r"\bnoticable",     "TYPO",  "noticeable"),
    (r"\bpriviledge",    "TYPO",  "privilege"),
    (r"\bpublically",    "TYPO",  "publicly"),
    (r"\buntill",        "TYPO",  "until"),
]

# Dead-code patterns are case-insensitive and don't use word boundaries (since
# they include the punctuation, e.g. ``TODO: remove``).
DEAD_CODE_PATTERNS: list[tuple[str, str, str]] = [
    (r"TODO\s*:\s*remove",        "DEAD_CODE", "remove or convert to issue"),
    (r"FIXME\s*:\s*delete",       "DEAD_CODE", "remove or convert to issue"),
    (r"XXX\s*:\s*remove",         "DEAD_CODE", "remove or convert to issue"),
]

# Inline allowlist: any line containing this token is ignored.
ALLOW_LINE_TOKEN = "lint-disable-line"


# ── File-type scoping ──────────────────────────────────────────────────────

INCLUDED_EXTS: set[str] = {
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".html", ".scss",
    ".md",
    ".yaml", ".yml",
    ".sh",
}

# Patterns (git ls-files style globs) for paths that should be excluded even
# if tracked. Each entry is checked with fnmatch.
EXCLUDED_PATH_PATTERNS: list[str] = [
    # Submodules: don't lint code that's owned by other repos.
    "libs/django-fusion/*",
    "libs/ceptor-ai/*",
    "libs/django-bolt/*",
    # Backup / archive snapshots — not actively maintained code.
    "backups/**",
    "archives/**",
    "**/backups/**",
    "**/archives/**",
    # Lock files (auto-generated, lots of hashes).
    "uv.lock",
    "**/uv.lock",
    "**/package-lock.json",
    "**/pnpm-lock.yaml",
    "**/yarn.lock",
    # Fixture / seed / test-data dumps.
    "**/dump-data.json",
    "**/fixtures/**",
    "**/test-data/**",
    "**/snapshots/**",
    # Standard ignore paths.
    "**/.git/**",
    "**/node_modules/**",
    "**/.venv/**",
    "**/__pycache__/**",
    "**/dist/**",
    "**/build/**",
    "**/.next/**",
]


def _is_excluded(rel_path: str) -> bool:
    """Return True if ``rel_path`` matches any exclusion pattern.

    Optimised: ``fnmatch`` is only used for the ``**``-prefixed patterns.
    The common no-wildcard prefixes are checked with ``startswith`` which
    is an order of magnitude faster on large repos.
    """
    import fnmatch

    # ── Fast-path: literal-prefix checks (no wildcards) ────────────────────
    prefixes = (
        "libs/django-fusion/",
        "libs/ceptor-ai/",
        "libs/django-bolt/",
        "backups/",
        "archives/",
        "uv.lock",
    )
    for pfx in prefixes:
        if rel_path == pfx or rel_path.startswith(pfx):
            return True

    # ── Slow-path: full glob match for the rest ─────────────────────────────
    for pat in EXCLUDED_PATH_PATTERNS:
        if fnmatch.fnmatch(rel_path, pat):
            return True
    return False


def _list_tracked_files() -> list[str]:
    """Return git-tracked files filtered by extension and exclusions.

    Uses ``git ls-files`` with per-extension patterns so the command itself
    does the filtering — much faster than post-filtering a giant list when the
    repo has thousands of files.
    """
    # Strip leading "." from each ext to form valid git pathspec patterns.
    patterns = [f"*.{ext.lstrip('.')}" for ext in INCLUDED_EXTS]
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z", "--", *patterns],
            capture_output=True,
            check=True,
            cwd=os.getcwd(),
        )
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: git ls-files failed: {exc}", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print("ERROR: git executable not found in PATH", file=sys.stderr)
        sys.exit(2)

    raw = out.stdout.decode("utf-8", errors="replace")
    files = [f for f in raw.split("\x00") if f]

    # Apply path exclusions post-hoc (cheap).
    return [f for f in files if not _is_excluded(f)]


def _list_staged_files() -> list[str]:
    """Return git-staged files (added/copied/modified/renamed/type-changed)
    filtered by extension and exclusions. Used by the pre-commit hook so
    we only scan what is about to be committed.
    """
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z"],
            capture_output=True,
            check=True,
            cwd=os.getcwd(),
        )
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: git diff --cached failed: {exc}", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print("ERROR: git executable not found in PATH", file=sys.stderr)
        sys.exit(2)

    raw = out.stdout.decode("utf-8", errors="replace")
    files = [f for f in raw.split("\x00") if f]

    # Filter by extension (git doesn't filter by extension in diff output).
    filtered: list[str] = []
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext not in INCLUDED_EXTS:
            continue
        if _is_excluded(f):
            continue
        filtered.append(f)
    return filtered


# ── Match data class ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Match:
    """A single regex match found in a file."""
    path: str
    line_no: int
    kind: str          # "TYPO" or "DEAD_CODE"
    matched: str       # the actual matched text
    suggestion: str    # what it should be / what to do
    line_text: str     # the full line (trimmed)


# ── Scanner ─────────────────────────────────────────────────────────────────


def _scan_file(path: str) -> Iterable[Match]:
    """Yield Match objects for all patterns found in ``path``."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
    except OSError:
        # Unreadable file: skip silently (likely a permission issue or
        # a broken symlink). Don't fail the whole check.
        return

    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        if ALLOW_LINE_TOKEN in raw_line:
            continue
        # Typos
        for pat, kind, suggestion in TYPO_PATTERNS:
            m = re.search(pat, raw_line, flags=re.IGNORECASE)
            if m:
                yield Match(
                    path=path,
                    line_no=line_no,
                    kind=kind,
                    matched=m.group(0),
                    suggestion=suggestion,
                    line_text=raw_line.strip(),
                )
        # Dead code
        for pat, kind, suggestion in DEAD_CODE_PATTERNS:
            m = re.search(pat, raw_line, flags=re.IGNORECASE)
            if m:
                yield Match(
                    path=path,
                    line_no=line_no,
                    kind=kind,
                    matched=m.group(0),
                    suggestion=suggestion,
                    line_text=raw_line.strip(),
                )


def run_check(mode: str = "tracked") -> list[Match]:
    """Scan eligible files and return every match found.

    Args:
        mode: ``"tracked"`` (default) scans all git-tracked files — used by CI.
              ``"staged"`` scans only files staged for commit — used by the
              pre-commit hook for fast feedback.
    """
    if mode == "staged":
        files = _list_staged_files()
    else:
        files = _list_tracked_files()
    matches: list[Match] = []
    for f in files:
        matches.extend(_scan_file(f))
    return matches


# ── Reporter ────────────────────────────────────────────────────────────────


def print_report(matches: list[Match]) -> None:
    """Print a human-friendly report and exit non-zero if matches present."""
    if not matches:
        print("✓ check_typos_and_deadcode: 0 matches")
        return

    print(f"✗ check_typos_and_deadcode: {len(matches)} match(es) found")
    print()
    by_kind: dict[str, list[Match]] = {}
    for m in matches:
        by_kind.setdefault(m.kind, []).append(m)

    for kind in ("TYPO", "DEAD_CODE"):
        items = by_kind.get(kind, [])
        if not items:
            continue
        print(f"── {kind} ({len(items)}) ──")
        for m in items:
            print(f"  {m.path}:{m.line_no}  '{m.matched}'  →  {m.suggestion}")
            # Show the offending line (trimmed to 100 chars)
            line_preview = m.line_text[:100]
            if len(m.line_text) > 100:
                line_preview += "..."
            print(f"    │ {line_preview}")
        print()


def main() -> int:
    # Allow CI bypass via env var (e.g. emergency hotfixes, vendored content).
    if os.environ.get("SKIP_LINT", "").lower() in ("1", "true", "yes"):
        print("⚠ SKIP_LINT=1 — bypassing typo/dead-code check")
        return 0

    # Mode: ``--staged`` scans staged files only (pre-commit hook).
    # Default scans all tracked files (CI).
    mode = "tracked"
    if "--staged" in sys.argv:
        mode = "staged"

    matches = run_check(mode=mode)
    print_report(matches)
    return 1 if matches else 0


if __name__ == "__main__":
    sys.exit(main())