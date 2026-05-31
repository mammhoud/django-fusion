#!/usr/bin/env python3
"""Load all site dump fixtures with clear logs.

The script is intentionally standalone so Docker entrypoints, Make targets, and
manual operators can run the same fixture loading process for any website.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def bootstrap_workspace() -> Path:
    """Ensure standalone script execution can import workspace modules."""
    repo_root = Path(__file__).resolve().parents[2]
    os.chdir(repo_root)
    path_text = str(repo_root)
    # Ensure the workspace root is at the beginning of sys.path
    # to override any site-specific paths that may be set by the container
    if path_text in sys.path:
        sys.path.remove(path_text)
    sys.path.insert(0, path_text)
    return repo_root


def configure(site: str) -> None:
    repo_root = bootstrap_workspace()

    from configs.site import configure_site_environment, site_dir_for

    configure_site_environment(site)
    site_dir = site_dir_for(site)
    for path in (site_dir, repo_root):
        path_text = str(path)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


def fixture_dirs() -> list[Path]:
    from django.conf import settings

    dirs: list[Path] = []
    for raw_path in getattr(settings, "FIXTURE_DIRS", []):
        path = Path(raw_path)
        if path.exists() and path not in dirs:
            dirs.append(path)
    base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd()))
    fallback = base_dir / "assets" / "fixtures"
    if fallback.exists() and fallback not in dirs:
        dirs.append(fallback)
    return dirs


def ordered_fixtures(include_extra: bool) -> list[Path]:
    found: list[Path] = []
    for directory in fixture_dirs():
        candidates: list[Path] = []
        primary = directory / "dump-data.json"
        if primary.exists():
            candidates.append(primary)
        candidates.extend(sorted(directory.glob("*dump*.json")))
        if include_extra:
            candidates.extend(directory / name for name in ("initial_choices.json", "users.json"))
        for path in candidates:
            if path.exists() and path not in found:
                found.append(path)
    return found


def wagtail_page_count() -> int | None:
    try:
        from wagtail.models import Page

        return Page.objects.count()
    except Exception as exc:  # pragma: no cover - diagnostic only
        print(f"⚠️  Could not count Wagtail pages before fixture load: {exc}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=os.getenv("DJANGO_SITE") or os.getenv("DJANGO_WEBSITE") or os.getenv("WEBSITE") or "ctc-research.com")
    parser.add_argument("--force", action="store_true", help="Load dump fixtures even when Wagtail already has content.")
    parser.add_argument("--include-extra", action="store_true", help="Also load non-dump bootstrap fixtures such as users and choices.")
    parser.add_argument("--list", action="store_true", help="Only list the fixtures that would be loaded.")
    args = parser.parse_args()

    configure(args.site)

    import django
    from django.core.management import call_command

    django.setup()

    fixtures = ordered_fixtures(args.include_extra)
    if not fixtures:
        print("ℹ️  No dump fixtures found for this site.")
        return 0

    if args.list:
        for fixture in fixtures:
            print(f"📦 {fixture}")
        print(f"✅ Found {len(fixtures)} fixture(s).")
        return 0

    page_count = wagtail_page_count()
    if page_count is not None and page_count > 2 and not args.force:
        print(f"ℹ️  Skipping dump fixture load because Wagtail already has {page_count} pages. Use --force to reload.")
        return 0

    failures = 0
    for fixture in fixtures:
        print(f"📂 Loading fixture: {fixture}")
        try:
            call_command("loaddata", str(fixture), ignorenonexistent=True, verbosity=1)
        except Exception as exc:  # keep trying so logs show every bad fixture
            failures += 1
            print(f"❌ Failed to load {fixture}: {exc}")

    if failures:
        print(f"❌ {failures} fixture(s) failed to load.")
        return 1
    print(f"✅ Loaded {len(fixtures)} fixture(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
