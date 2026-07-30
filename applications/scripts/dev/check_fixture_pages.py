#!/usr/bin/env python3
"""
check_fixture_pages.py — Validate that FIXTURE_PAGES in E2E tests match dump-data.json.

Compares the `FIXTURE_PAGES` constants defined in fixture-content.spec.ts
against the English-language (locale_id=1) Wagtail page records in the
corresponding dump-data.json fixture file.

If any slug, title, or seo_title mismatches are found, the script exits
with a non-zero code and prints details.

Usage:
    python3 applications/scripts/dev/check_fixture_pages.py        # Check both CMS and LMS
    python3 applications/scripts/dev/check_fixture_pages.py --cms  # CMS only
    python3 applications/scripts/dev/check_fixture_pages.py --lms  # LMS only
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]


# ── Site configurations ──────────────────────────────────────────────────────

SiteConfig = dict[str, Any]

SITES: dict[str, SiteConfig] = {
    "cms": {
        "label": "CMS Fusion",
        "fixture_path": REPO_ROOT
        / "projects"
        / "cms-fusion"
        / "backend"
        / "assets"
        / "fixtures"
        / "dump-data.json",
        "test_path": REPO_ROOT
        / "projects"
        / "cms-fusion"
        / "frontend"
        / "tests"
        / "e2e"
        / "fixture-content.spec.ts",
    },
    "lms": {
        "label": "LMS Fusion",
        "fixture_path": REPO_ROOT
        / "projects"
        / "lms-fusion"
        / "backend"
        / "assets"
        / "fixtures"
        / "dump-data.json",
        "test_path": REPO_ROOT
        / "projects"
        / "lms-fusion"
        / "frontend"
        / "tests"
        / "e2e"
        / "fixture-content.spec.ts",
    },
}


# ── Helpers ──────────────────────────────────────────────────────────────────


def load_fixture(path: Path) -> list[dict[str, Any]]:
    """Load a dump-data.json fixture file and return the parsed objects."""
    if not path.exists():
        print(f"  ❌ Fixture not found: {path}")
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_fixture_pages(
    fixture: list[dict[str, Any]],
) -> dict[str, dict[str, str]]:
    """Extract English (locale_id=1) Wagtail page records from the fixture.

    Returns a dict keyed by slug, with each value containing title and seo_title.
    """
    pages: dict[str, dict[str, str]] = {}
    for obj in fixture:
        fields = obj.get("fields", {})
        slug = fields.get("slug", "")
        title = fields.get("title", "")
        if not slug or not title:
            continue

        # Only include pages that have a locale FK to the English locale (id=1).
        # Skip root and non-content pages.
        if fields.get("locale") != 1:
            continue

        seo_title = fields.get("seo_title", "")
        pages[slug] = {
            "title": title,
            "seo_title": seo_title,
        }
    return pages


def parse_fixture_pages_from_ts(
    content: str,
) -> dict[str, dict[str, str]]:
    """Parse the FIXTURE_PAGES constant from a fixture-content.spec.ts file.

    Uses regex to extract the TypeScript object literal keys and their
    title/seoTitle string values.
    """
    pages: dict[str, dict[str, str]] = {}

    # Find the FIXTURE_PAGES declaration block.
    # We look for 'const FIXTURE_PAGES' and capture everything up to the
    # closing semicolon or the next top-level declaration.
    match = re.search(
        r"const\s+FIXTURE_PAGES\s*:\s*Record\s*<[^>]+>\s*=\s*\{",
        content,
    )
    if not match:
        print("  ❌ Could not find FIXTURE_PAGES declaration in test file")
        return pages

    start = match.end()
    # Find the matching closing brace by tracking nesting depth.
    depth = 1
    end = start
    while end < len(content) and depth > 0:
        ch = content[end]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        end += 1
    block = content[start : end - 1]  # Exclude the closing '}'

    # Now extract each slug entry.  Pattern:
    #   slug: { title: '...', seoTitle?: '...'? }
    entry_pattern = re.compile(
        r"""
        \{\s*                                          # opening brace
        title:\s*   '(?P<title>[^']*)'                  # title field
        (?:,\s*seoTitle\??:\s*'(?P<seo>[^']*)')?       # optional seoTitle
        \s*\}\s*,?                                      # closing brace, optional comma
        """,
        re.VERBOSE,
    )

    # Split the block by top-level keys (e.g., "home:", "about:", etc.)
    # We split at word boundaries followed by colon outside braces.
    key_pattern = re.compile(r"(\w+)\s*:")
    pos = 0
    for key_match in key_pattern.finditer(block):
        key = key_match.group(1)
        val_start = key_match.end()
        # Find the value (nested object).  Skip past the opening { and track depth.
        if val_start < len(block) and block[val_start] == "{":
            depth = 1
            val_end = val_start + 1
            while val_end < len(block) and depth > 0:
                ch = block[val_end]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                val_end += 1
            value_str = block[val_start:val_end]

            entry_match = entry_pattern.match(value_str)
            if entry_match:
                title = entry_match.group("title")
                seo = entry_match.group("seo") or ""
                pages[key] = {"title": title, "seo_title": seo}

    return pages


def check_site(site_name: str, cfg: SiteConfig) -> bool:
    """Check a single site's test expectations against its fixture data.

    Returns True if all checks pass, False otherwise.
    """
    label = cfg["label"]
    fixture_path = cfg["fixture_path"]
    test_path = cfg["test_path"]

    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Fixture: {fixture_path.relative_to(REPO_ROOT)}")
    print(f"  Test:    {test_path.relative_to(REPO_ROOT)}")

    # ── Load fixture ──────────────────────────────────────────────────
    fixture = load_fixture(fixture_path)
    if not fixture:
        return False

    fixture_pages = extract_fixture_pages(fixture)
    if not fixture_pages:
        print("  ❌ No English (locale_id=1) pages found in fixture")
        return False

    print(f"  Found {len(fixture_pages)} English fixture pages:")
    for slug, info in sorted(fixture_pages.items()):
        print(f"    {slug:<12} → title={info['title']!r}")

    # ── Load test expectations ────────────────────────────────────────
    if not test_path.exists():
        print(f"  ❌ Test file not found: {test_path}")
        return False

    test_content = test_path.read_text(encoding="utf-8")
    test_pages = parse_fixture_pages_from_ts(test_content)
    if not test_pages:
        print("  ❌ Could not parse FIXTURE_PAGES from test file")
        return False

    print(f"\n  Test file defines {len(test_pages)} FIXTURE_PAGES entries:")
    for slug, info in sorted(test_pages.items()):
        seo_display = f", seoTitle={info['seo_title']!r}" if info["seo_title"] else ""
        print(f"    {slug:<12} → title={info['title']!r}{seo_display}")

    # ── Compare ───────────────────────────────────────────────────────
    print(f"\n  {'─'*56}")
    all_pass = True

    for slug, expected in sorted(test_pages.items()):
        actual = fixture_pages.get(slug)
        if actual is None:
            print(f"  ❌ {slug}: not found in fixture (present in test, missing from dump-data.json)")
            all_pass = False
            continue

        issues: list[str] = []
        if expected["title"] != actual["title"]:
            issues.append(
                f"title mismatch: expected {expected['title']!r}, fixture has {actual['title']!r}"
            )
        if expected["seo_title"] and expected["seo_title"] != actual["seo_title"]:
            issues.append(
                f"seo_title mismatch: expected {expected['seo_title']!r}, fixture has {actual['seo_title']!r}"
            )

        if issues:
            print(f"  ❌ {slug}:")
            for issue in issues:
                print(f"       {issue}")
            all_pass = False
        else:
            print(f"  ✅ {slug}: title={actual['title']!r}, seo={actual['seo_title']!r}")

    # ── Check for fixture pages missing from test ─────────────────────
    test_slugs = set(test_pages.keys())
    for slug, info in sorted(fixture_pages.items()):
        if slug not in test_slugs and slug not in ("root",):
            print(f"  ⚠️  {slug}: fixture has page \"{info['title']}\" but test has no FIXTURE_PAGES entry (omit if intentional)")

    return all_pass


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    # Determine which sites to check
    args = sys.argv[1:]
    check_all = not any(arg.startswith("--") for arg in args)
    check_cms = check_all or "--cms" in args
    check_lms = check_all or "--lms" in args

    results: dict[str, bool] = {}

    if check_cms:
        results["cms"] = check_site("cms", SITES["cms"])
    if check_lms:
        results["lms"] = check_site("lms", SITES["lms"])

    # ── Summary ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    all_pass = all(results.values()) if results else False
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {SITES[name]['label']}: {status}")

    print(f"\n  Overall: {'✅ PASS' if all_pass else '❌ FAIL'}")
    print(f"{'='*60}\n")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
