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
    repo_root = Path(__file__).resolve().parents[3]
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
    fallback = base_dir.parent / "assets" / "fixtures"
    if fallback.exists() and fallback not in dirs:
        dirs.append(fallback)
    # Add repository assets fixtures directory
    repo_root = Path(__file__).resolve().parents[3]
    extra = repo_root / "tests" / "fixtures"
    if extra.exists() and extra not in dirs:
        dirs.append(extra)
    return dirs


def ordered_fixtures(include_extra: bool, include_dumps: bool) -> list[Path]:
    found: list[Path] = []
    for directory in fixture_dirs():
        candidates: list[Path] = []
        if include_dumps:
            primary = directory / "dump-data.json"
            if primary.exists():
                candidates.append(primary)
            candidates.extend(sorted(directory.glob("*dump*.json")))
        if include_extra:
            preferred = [
                directory / "auth" / "group_dummy.json",
                directory / "auth" / "user_dummy.json",
                directory / "sites" / "site_dummy.json",
                directory / "initial_choices.json",
                directory / "users.json",
            ]
            candidates.extend(preferred)
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


def clear_duplicate_permissions():
    """Delete all GroupPagePermission entries to avoid duplicate key errors before loading fixtures."""
    from wagtail.models import GroupPagePermission
    # Remove all existing permissions to ensure a clean import
    GroupPagePermission.objects.all().delete()
    """Ensure the default Site has a HomePage as root_page."""
    from wagtail.models import Site, Page
    from django.contrib.contenttypes.models import ContentType
    try:
        site = Site.objects.get(is_default_site=True)
    except Site.DoesNotExist:
        print("⚠️ No default Site found")
        return
    # If root_page is missing or not a Page, set/create HomePage
    if not site.root_page_id or not isinstance(site.root_page.specific, Page):
        try:
            from www.core.content.models.pages.home import HomePage
        except Exception as e:
            print(f"Error importing HomePage: {e}")
            return
        homepage_ct = ContentType.objects.get_for_model(HomePage)
        home = Page.objects.filter(content_type=homepage_ct, depth=2).first()
        if not home:
            root = Page.objects.get(depth=1)
            home = HomePage(title="Home", slug="home")
            root.add_child(instance=home)
        site.root_page = home
        site.save()
        print(f"✓ Site root set to HomePage: {home.title}")
    else:
        print("✓ Site root_page already valid")





def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site")
    parser.add_argument("--include-extra", action="store_true")
    parser.add_argument("--include-dumps", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    configure(args.site)

    import django
    from django.core.management import call_command

    django.setup()

    include_dumps = args.include_dumps or args.force
    fixtures = ordered_fixtures(args.include_extra, include_dumps)
    if not fixtures:
        print("ℹ️  No dump fixtures found for this site.")
        return 0

    if args.list:
        for fixture in fixtures:
            print(f"📦 {fixture}")
        print(f"✅ Found {len(fixtures)} fixture(s).")
        return 0

    # Clear duplicate permissions before loading
    clear_duplicate_permissions()

    page_count = wagtail_page_count()
    if include_dumps and page_count is not None and page_count > 2 and not args.force:
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

    # Run homepage fix after loading
    run_fix_homepage()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
