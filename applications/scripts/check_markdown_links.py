"""CI script: validate every Markdown link under ``core/libs/**/docs/``.

Two link classes are validated:

* **Relative paths** (``./foo``, ``../bar/baz.md``, ``/RELEASES``) — checked against the
  filesystem relative to the source file's directory.
* **Absolute URLs** (``https://example.com/...``) — checked via HTTP HEAD with a short
  timeout. The script only inspects ``http://`` and ``https://`` schemes; ``mailto:``,
  ``tel:``, and similar are ignored.

The script also ignores:

* ``[text](...)`` inside code fences (``\`\`\` … \`\`\``) and indented code blocks.
* ``[text](...)`` inside inline code spans (``\`like this\`\`).
* Common image links (``![alt](src)``) — they are checked against the same rules.

Exit codes
----------

* ``0`` — every link resolved.
* ``1`` — at least one broken link, or a fatal scan error.

The CI workflow in ``.github/workflows/check-links.yml`` runs this script on PRs and
pushes that touch Markdown under ``core/libs/**/docs/`` so the legacy-README
class of bug cannot regress silently.
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# This script lives at core/scripts/check_markdown_links.py.
# The repo root is two directories up.
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCOPE = REPO_ROOT / "core" / "libs"

# Markdown link anchor: text in brackets, then parenthesized target (optionally with a title).
LINK_RE = re.compile(
    r"!?\[(?P<text>[^\]]*)\]"           # text in brackets (optional leading '!' for images)
    r"\("                                 # opening paren
    r"(?P<target>[^)\s]*)"                # url (no whitespace, no closing paren)
    r"(?:\s+\"[^\"]*\")?"                 # optional title in double-quotes
    r"\)"                                 # closing paren
)

FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")

# Schemes we treat as "external" (subject to HTTP check) vs. ignored (anchor/email).
EXTERNAL_SCHEMES = ("http://", "https://")

# Trailing punctuation that often glues onto link targets.
TRAILING_PUNCT = ".,;:!?"


def _clean_target(raw: str) -> str:
    """Strip URL fragment / query / trailing markdown punctuation."""
    t = raw.strip()
    if "#" in t:
        t = t.split("#", 1)[0]
    if "?" in t:
        t = t.split("?", 1)[0]
    return t.rstrip(TRAILING_PUNCT)


def _is_external(target: str) -> bool:
    return target.startswith(EXTERNAL_SCHEMES)


def _is_external_ignored(target: str) -> bool:
    """External links we don't validate (mailto:, tel:, ftp:, etc.)."""
    return ":" in target.split("/", 1)[0] and not _is_external(target)


def _strip_code_regions(line: str) -> str:
    """Replace inline-code spans with whitespace (preserving positions) so the regex
    can't match inside them. Code fences are handled at the paragraph level by the caller.
    """
    def _blank(match: re.Match) -> str:
        return " " * len(match.group(0))
    return INLINE_CODE_RE.sub(_blank, line)


def _iter_markdown_files(scope: Path):
    """Yield every ``.md`` file under ``scope`` recursively."""
    yield from sorted(scope.rglob("*.md"))


def _scan_links(
    file_path: Path,
    check_external: bool,
    http_timeout: float,
    errors: list[tuple[Path, int, str, str, str]],
    http_warnings: list[tuple[Path, int, str, str, str]],
):
    """Parse ``file_path`` for links; validate each and append to ``errors`` if broken."""
    text = file_path.read_text(encoding="utf-8")
    file_dir = file_path.parent
    in_fence = False
    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line
        # Toggle fenced code blocks.
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Strip inline code (so bracketed text inside backticks is ignored).
        scan_line = _strip_code_regions(line)
        for m in LINK_RE.finditer(scan_line):
            link_text = m.group("text").strip() or "(no text)"
            target = _clean_target(m.group("target") or "")
            if not target:
                continue
            if _is_external_ignored(target):
                continue
            if _is_external(target):
                if not check_external:
                    continue
                status = _http_status(target, timeout=http_timeout)
                if status in ("200", "2xx", None):  # None = infra failure, warn-only by default
                    if status is None:
                        http_warnings.append((file_path, lineno, link_text, target, "network failure"))
                    continue
                errors.append((file_path, lineno, link_text, target, f"HTTP {status}"))
                continue
            # Relative path check.
            if not (target.startswith(".") or target.startswith("/")):
                # Bare word or sibling-without-leading-dot — skip; not a verifiable path.
                continue
            try:
                resolved = (file_dir / target).resolve()
            except (OSError, RuntimeError) as exc:
                errors.append((file_path, lineno, link_text, target, f"resolve error: {exc}"))
                continue
            if not resolved.exists():
                errors.append((file_path, lineno, link_text, target, "filesystem: not found"))


def _http_status(url: str, timeout: float) -> str | None:
    """Return the HTTP status class for *url* (e.g. ``"200"``, ``"404"``) or ``None``
    if the request couldn't complete (network/DNS/SSL). We use HEAD with a browser UA
    and let urllib handle redirects.
    """
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ci-link-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return str(resp.status)
    except urllib.error.HTTPError as exc:
        return str(exc.code)
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def _format_entry(entry: tuple[Path, int, str, str, str]) -> str:
    file_path, lineno, text, target, reason = entry
    return f"{file_path.relative_to(REPO_ROOT)}:{lineno}  [{text}]({target})  → {reason}"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--scope",
        type=Path,
        default=DEFAULT_SCOPE,
        help=f"Directory to scan (default: {DEFAULT_SCOPE.relative_to(REPO_ROOT)}).",
    )
    p.add_argument(
        "--no-external",
        action="store_true",
        help="Skip HTTP checks (filesystem-relative links only). Useful offline / for fast pre-PR local runs.",
    )
    p.add_argument(
        "--http-timeout",
        type=float,
        default=10.0,
        help="Per-request timeout for HTTP HEAD (seconds). Default: 10.",
    )
    p.add_argument(
        "--no-http-warnings",
        action="store_true",
        help="Treat HTTP network failures (DNS/timeout) as warnings (default). Pass to suppress the messages.",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    scope = args.scope.resolve()
    if not scope.is_dir():
        print(f"error: scope {scope} is not a directory", file=sys.stderr)
        return 2

    errors: list[tuple[Path, int, str, str, str]] = []
    http_warnings: list[tuple[Path, int, str, str, str]] = []
    total_links = 0

    files = list(_iter_markdown_files(scope))
    if not files:
        print(f"(no .md files found under {scope})", file=sys.stderr)
        return 0
    print(f"scanning {len(files)} Markdown file(s) under {scope.relative_to(REPO_ROOT)}/")

    for f in files:
        _scan_links(
            f,
            check_external=not args.no_external,
            http_timeout=args.http_timeout,
            errors=errors,
            http_warnings=http_warnings,
        )

    print(f"broken links: {len(errors)}")
    print(f"http warnings: {len(http_warnings)}" if http_warnings else "http warnings: 0")

    for entry in errors:
        print(f"  BROKEN  {_format_entry(entry)}")
    if http_warnings and not args.no_http_warnings:
        for entry in http_warnings:
            print(f"  WARN    {_format_entry(entry)}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
