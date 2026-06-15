#!/usr/bin/env python3
"""
Template validation script for the ecosystem-wide architectural refactoring.

Commands:
  check_no_package_templates   - Scan venv/libs/ for any .html files and report violations
  check_template_structure     - Verify both projects have consistent top-level template dirs
  verify_template_resolution   - Check that template names referenced in Python render() calls
                                 and {% include %}/{% extends %} tags exist on disk

Usage:
  python scripts/validate_templates.py check_no_package_templates
  python scripts/validate_templates.py check_template_structure
  python scripts/validate_templates.py verify_template_resolution
"""

import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WORKSPACE_ROOT = Path(__file__).parent.parent
VENV_LIBS = WORKSPACE_ROOT / "venv" / "libs"
CTC_PROJECT = WORKSPACE_ROOT / "ctc-research.com"
STRUCTA_PROJECT = WORKSPACE_ROOT / "structa.cloud"

# Packages to scan (exclude .venv, node_modules, etc.)
PACKAGES = [
    VENV_LIBS / "django-osoul" / "src" / "django_osoul",
    VENV_LIBS / "django-rseal" / "src" / "django_rseal",
    VENV_LIBS / "django-grep" / "src" / "django_grep",
    VENV_LIBS / "nawaai" / "crafts_ai",
]

# Template directories in each project
CTC_TEMPLATE_DIRS = [
    CTC_PROJECT / "apps" / "templates",
    CTC_PROJECT / "assets" / "templates" / "layout",  # layout/ is a separate DIRS entry
    CTC_PROJECT / "assets" / "templates",
    CTC_PROJECT / "core" / "templates",
    CTC_PROJECT / "components",
    CTC_PROJECT / "email_templates",
]

STRUCTA_TEMPLATE_DIRS = [
    STRUCTA_PROJECT / "apps" / "templates",
    STRUCTA_PROJECT / "assets" / "templates" / "layout",  # layout/ is a separate DIRS entry
    STRUCTA_PROJECT / "assets" / "templates",
    STRUCTA_PROJECT / "core" / "templates",
    STRUCTA_PROJECT / "components",
    STRUCTA_PROJECT / "email_templates",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_html_files(directory: Path) -> list[Path]:
    """Recursively find all .html files under a directory."""
    if not directory.exists():
        return []
    return list(directory.rglob("*.html"))


def collect_all_template_names(template_dirs: list[Path]) -> set[str]:
    """
    Collect all template names (relative paths) from a list of template directories.
    Returns names as they would be referenced in templates (e.g. 'auth/login.html').
    """
    names: set[str] = set()
    for tdir in template_dirs:
        if not tdir.exists():
            continue
        for html_file in tdir.rglob("*.html"):
            rel = html_file.relative_to(tdir)
            names.add(str(rel))
    return names


def find_python_files(directory: Path) -> list[Path]:
    """Recursively find all .py files under a directory."""
    if not directory.exists():
        return []
    return list(directory.rglob("*.py"))


# ---------------------------------------------------------------------------
# Command 1: check_no_package_templates
# ---------------------------------------------------------------------------

def check_no_package_templates() -> int:
    """
    Scan venv/libs/ packages for any .html files.
    Reports violations (templates found in packages).
    Returns exit code: 0 = no violations, 1 = violations found.
    """
    print("=" * 70)
    print("CHECK: No templates in venv/libs/ packages")
    print("=" * 70)
    print()

    violations: list[tuple[str, Path]] = []

    for package_dir in PACKAGES:
        if not package_dir.exists():
            print(f"  [SKIP] Package directory not found: {package_dir}")
            continue

        html_files = find_html_files(package_dir)
        for html_file in sorted(html_files):
            # Determine relative path from workspace root
            try:
                rel = html_file.relative_to(WORKSPACE_ROOT)
            except ValueError:
                rel = html_file
            package_name = package_dir.name
            violations.append((package_name, rel))

    if not violations:
        print("✅ PASS: No HTML templates found in any venv/libs/ package.")
        print()
        return 0

    print(f"❌ FAIL: Found {len(violations)} template(s) in venv/libs/ packages.")
    print()
    print("Templates MUST stay in projects (ctc-research.com/templates/,")
    print("structa.cloud/templates/), NOT in venv/libs/ packages.")
    print()

    # Group by package
    by_package: dict[str, list[Path]] = {}
    for pkg_name, rel_path in violations:
        by_package.setdefault(pkg_name, []).append(rel_path)

    for pkg_name, paths in sorted(by_package.items()):
        print(f"  Package: {pkg_name} ({len(paths)} template(s))")
        for p in sorted(paths):
            print(f"    - {p}")
        print()

    print("Fix: Move each template to the appropriate project's templates/ directory")
    print("     and update all {% include %}, {% extends %}, and render() references.")
    print()
    return 1


# ---------------------------------------------------------------------------
# Command 2: check_template_structure
# ---------------------------------------------------------------------------

EXPECTED_TOP_LEVEL_DIRS = {
    "auth",
    "registration",
    "layout",
    "partials",
    "emails",
    "email",
    "components",
    "blog",
    "home",
    "courses",
    "learning",
    "common",
    "newsletter",
    "certification",
    "profile",
    "search",
    "content",
    "pages",
    "base",
}


def get_top_level_template_dirs(template_dirs: list[Path]) -> set[str]:
    """Get the set of top-level subdirectory names across all template dirs."""
    top_level: set[str] = set()
    for tdir in template_dirs:
        if not tdir.exists():
            continue
        for item in tdir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                top_level.add(item.name)
    return top_level


def check_template_structure() -> int:
    """
    Verify both projects have similar top-level template directory structure.
    Returns exit code: 0 = consistent, 1 = inconsistencies found.
    """
    print("=" * 70)
    print("CHECK: Consistent template structure between projects")
    print("=" * 70)
    print()

    ctc_dirs = get_top_level_template_dirs(CTC_TEMPLATE_DIRS)
    structa_dirs = get_top_level_template_dirs(STRUCTA_TEMPLATE_DIRS)

    print(f"ctc-research.com top-level template dirs ({len(ctc_dirs)}):")
    for d in sorted(ctc_dirs):
        print(f"  - {d}")
    print()

    print(f"structa.cloud top-level template dirs ({len(structa_dirs)}):")
    for d in sorted(structa_dirs):
        print(f"  - {d}")
    print()

    # Find dirs in one but not the other
    only_in_ctc = ctc_dirs - structa_dirs
    only_in_structa = structa_dirs - ctc_dirs
    in_both = ctc_dirs & structa_dirs

    print(f"Shared top-level dirs: {len(in_both)}")
    print(f"Only in ctc-research.com: {sorted(only_in_ctc)}")
    print(f"Only in structa.cloud: {sorted(only_in_structa)}")
    print()

    # Check for missing template dirs in each project
    issues: list[str] = []

    # Both projects should have auth/registration templates
    auth_dirs = {"auth", "registration"}
    ctc_has_auth = bool(ctc_dirs & auth_dirs)
    structa_has_auth = bool(structa_dirs & auth_dirs)

    if not ctc_has_auth:
        issues.append("ctc-research.com is missing auth/registration template directory")
    if not structa_has_auth:
        issues.append("structa.cloud is missing auth/registration template directory")

    # Both should have layout or partials
    layout_dirs = {"layout", "partials"}
    ctc_has_layout = bool(ctc_dirs & layout_dirs)
    structa_has_layout = bool(structa_dirs & layout_dirs)

    if not ctc_has_layout:
        issues.append("ctc-research.com is missing layout/partials template directory")
    if not structa_has_layout:
        issues.append("structa.cloud is missing layout/partials template directory")

    if issues:
        print(f"❌ FAIL: {len(issues)} structural inconsistency(ies) found:")
        for issue in issues:
            print(f"  - {issue}")
        print()
        return 1

    print("✅ PASS: Both projects have consistent template structure.")
    print()
    return 0


# ---------------------------------------------------------------------------
# Command 3: verify_template_resolution
# ---------------------------------------------------------------------------

INCLUDE_EXTENDS_RE = re.compile(
    r"""{%[-\s]*(?:include|extends)\s+["']([^"']+)["']""",
    re.IGNORECASE,
)

RENDER_RE = re.compile(
    r"""render\s*\(\s*request\s*,\s*["']([^"']+\.html)["']""",
    re.IGNORECASE,
)

RENDER_TO_STRING_RE = re.compile(
    r"""render_to_string\s*\(\s*["']([^"']+\.html)["']""",
    re.IGNORECASE,
)

GET_TEMPLATE_RE = re.compile(
    r"""get_template\s*\(\s*["']([^"']+\.html)["']""",
    re.IGNORECASE,
)


def extract_template_refs_from_html(html_file: Path) -> list[tuple[str, int, str]]:
    """Extract template references from {% include %} and {% extends %} tags.
    Skips lines inside Django {# ... #} comments and HTML <!-- --> comments.
    """
    refs = []
    try:
        content = html_file.read_text(encoding="utf-8", errors="replace")
        in_comment_block = False
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            # Track {% comment %} / {% endcomment %} blocks
            if "{% comment %}" in stripped:
                in_comment_block = True
            if "{% endcomment %}" in stripped:
                in_comment_block = False
                continue
            if in_comment_block:
                continue
            # Skip Django inline comments {# ... #} and HTML comments
            if stripped.startswith("{#") or stripped.startswith("<!--"):
                continue
            for match in INCLUDE_EXTENDS_RE.finditer(line):
                refs.append((str(html_file), i, match.group(1)))
    except Exception:
        pass
    return refs


def extract_template_refs_from_python(py_file: Path) -> list[tuple[str, int, str]]:
    """Extract template references from Python render() calls.
    Skips commented-out lines (# ...).
    """
    refs = []
    try:
        content = py_file.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            # Skip Python comments
            if stripped.startswith("#"):
                continue
            for pattern in [RENDER_RE, RENDER_TO_STRING_RE, GET_TEMPLATE_RE]:
                for match in pattern.finditer(line):
                    refs.append((str(py_file), i, match.group(1)))
    except Exception:
        pass
    return refs


def verify_template_resolution() -> int:
    """
    Check that template names referenced in Python render() calls and
    {% include %}/{% extends %} tags exist on disk.
    Returns exit code: 0 = all resolved, 1 = broken references found.
    """
    print("=" * 70)
    print("CHECK: Template reference resolution")
    print("=" * 70)
    print()

    # Collect all available template names from both projects
    # Also scan app-level templates/ directories (APP_DIRS loader)
    ctc_app_template_dirs = [
        d for d in (CTC_PROJECT / "apps").rglob("templates")
        if d.is_dir()
    ]
    structa_app_template_dirs = [
        d for d in (STRUCTA_PROJECT / "apps").rglob("templates")
        if d.is_dir()
    ]

    ctc_templates = collect_all_template_names(CTC_TEMPLATE_DIRS + ctc_app_template_dirs)
    structa_templates = collect_all_template_names(STRUCTA_TEMPLATE_DIRS + structa_app_template_dirs)

    # Also collect from package app_directories (since APP_DIRS loader is used)
    package_templates: set[str] = set()
    for pkg_dir in PACKAGES:
        pkg_template_dir = pkg_dir / "templates"
        if pkg_template_dir.exists():
            for html_file in pkg_template_dir.rglob("*.html"):
                rel = html_file.relative_to(pkg_template_dir)
                package_templates.add(str(rel))
        # Also check comp/blocks for block templates
        comp_blocks_dir = pkg_dir / "comp" / "blocks"
        if comp_blocks_dir.exists():
            for html_file in comp_blocks_dir.rglob("*.html"):
                rel = html_file.relative_to(comp_blocks_dir.parent.parent)
                package_templates.add(str(rel))

    all_ctc_available = ctc_templates | package_templates
    all_structa_available = structa_templates | package_templates

    print(f"Available templates:")
    print(f"  ctc-research.com: {len(ctc_templates)} project + {len(package_templates)} package = {len(all_ctc_available)} total")
    print(f"  structa.cloud: {len(structa_templates)} project + {len(package_templates)} package = {len(all_structa_available)} total")
    print()

    broken_refs: list[tuple[str, int, str, str]] = []  # (file, line, ref, project)

    # Check ctc-research.com HTML templates
    for tdir in CTC_TEMPLATE_DIRS:
        for html_file in find_html_files(tdir):
            for src_file, line_no, ref in extract_template_refs_from_html(html_file):
                if ref not in all_ctc_available:
                    broken_refs.append((src_file, line_no, ref, "ctc-research.com"))

    # Check ctc-research.com Python files
    for py_dir in [CTC_PROJECT / "apps", CTC_PROJECT / "core", CTC_PROJECT / "configs"]:
        for py_file in find_python_files(py_dir):
            for src_file, line_no, ref in extract_template_refs_from_python(py_file):
                if ref not in all_ctc_available:
                    broken_refs.append((src_file, line_no, ref, "ctc-research.com"))

    # Check structa.cloud HTML templates
    for tdir in STRUCTA_TEMPLATE_DIRS:
        for html_file in find_html_files(tdir):
            for src_file, line_no, ref in extract_template_refs_from_html(html_file):
                if ref not in all_structa_available:
                    broken_refs.append((src_file, line_no, ref, "structa.cloud"))

    # Check structa.cloud Python files
    for py_dir in [STRUCTA_PROJECT / "apps", STRUCTA_PROJECT / "core", STRUCTA_PROJECT / "configs"]:
        for py_file in find_python_files(py_dir):
            for src_file, line_no, ref in extract_template_refs_from_python(py_file):
                if ref not in all_structa_available:
                    broken_refs.append((src_file, line_no, ref, "structa.cloud"))

    if not broken_refs:
        print("✅ PASS: All template references resolve correctly.")
        print()
        return 0

    # Deduplicate by (ref, project)
    seen: set[tuple[str, str]] = set()
    unique_broken: list[tuple[str, int, str, str]] = []
    for item in broken_refs:
        key = (item[2], item[3])
        if key not in seen:
            seen.add(key)
            # Skip third-party templates (wagtailadmin, mfa) - provided by installed packages
            if item[2].startswith("wagtailadmin/") or item[2].startswith("mfa/"):
                continue
            # Skip dynamic template references (contain template variable syntax)
            if item[2].endswith("/") or "|" in item[2]:
                continue
            # Skip email_templates/ references - used by email rendering, not Django template engine
            if item[2].startswith("email_templates/"):
                continue
            unique_broken.append(item)

    if not unique_broken:
        print("✅ PASS: All template references resolve correctly.")
        print()
        return 0

    print(f"⚠️  WARNING: Found {len(unique_broken)} potentially unresolved template reference(s).")
    print()
    print("Note: Some references may use dynamic template names (variables) or")
    print("      templates from third-party packages not scanned here.")
    print()

    by_project: dict[str, list[tuple[str, int, str]]] = {}
    for src_file, line_no, ref, project in unique_broken:
        by_project.setdefault(project, []).append((src_file, line_no, ref))

    for project, items in sorted(by_project.items()):
        print(f"  Project: {project} ({len(items)} reference(s))")
        for src_file, line_no, ref in sorted(items, key=lambda x: x[2]):
            # Make path relative to workspace
            try:
                rel_src = str(Path(src_file).relative_to(WORKSPACE_ROOT))
            except ValueError:
                rel_src = src_file
            print(f"    - '{ref}'")
            print(f"      at {rel_src}:{line_no}")
        print()

    return 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

COMMANDS = {
    "check_no_package_templates": check_no_package_templates,
    "check_template_structure": check_template_structure,
    "verify_template_resolution": verify_template_resolution,
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python {sys.argv[0]} <command>")
        print()
        print("Commands:")
        for cmd in COMMANDS:
            print(f"  {cmd}")
        return 1

    command = sys.argv[1]
    return COMMANDS[command]()


if __name__ == "__main__":
    sys.exit(main())
