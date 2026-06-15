#!/usr/bin/env python3
"""Verify a built site's runtime pages and collected assets."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse


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


def check_assets(strict: bool) -> int:
    from django.conf import settings

    failures = 0
    webpack_config = getattr(settings, "WEBPACK_LOADER", {}).get("DEFAULT", {})
    raw_stats_file = webpack_config.get("STATS_FILE", "")
    stats_file = Path(raw_stats_file) if raw_stats_file else None
    if stats_file and stats_file.exists() and stats_file.is_file():
        try:
            data = json.loads(stats_file.read_text())
            status = data.get("status", "unknown")
            print(f"✅ Webpack stats found: {stats_file} (status={status})")
        except json.JSONDecodeError as exc:
            print(f"❌ Webpack stats are invalid JSON: {stats_file}: {exc}")
            failures += 1
    else:
        message = f"Webpack stats file missing: {stats_file or '<unset>'}"
        print(("❌ " if strict else "⚠️  ") + message)
        failures += int(strict)

    raw_static_root = getattr(settings, "STATIC_ROOT", "") or ""
    static_root = Path(raw_static_root) if raw_static_root else None
    static_files = list(static_root.rglob("*")) if static_root and static_root.exists() else []
    static_file_count = sum(1 for path in static_files if path.is_file())
    if static_file_count:
        print(f"✅ Collected static files found: {static_file_count} files under {static_root}")
    else:
        message = f"No collected static files found under STATIC_ROOT={static_root or '<unset>'}"
        print(("❌ " if strict else "⚠️  ") + message)
        failures += int(strict)
    return failures


def page_path(page, wagtail_site) -> str | None:
    try:
        relative = page.relative_url(wagtail_site) if wagtail_site else page.url
    except Exception:
        relative = page.url
    if not relative:
        return None
    parsed = urlparse(relative)
    return parsed.path or "/"


def check_pages(strict_content: bool, strict_pages: bool) -> int:
    from django.test import Client

    try:
        from wagtail.models import Page, Site
    except ModuleNotFoundError as exc:
        message = f"Wagtail is not installed or not available: {exc}"
        print(("❌ " if strict_pages else "⚠️  ") + message)
        return int(strict_pages)

    failures = 0
    try:
        wagtail_site = Site.objects.filter(is_default_site=True).first() or Site.objects.first()
        pages = list(Page.objects.live().public().specific().order_by("path"))
    except Exception as exc:
        message = f"Wagtail pages could not be queried. Run migrations first: {exc}"
        print(("❌ " if strict_pages else "⚠️  ") + message)
        return int(strict_pages)

    host = wagtail_site.hostname if wagtail_site else "localhost"
    client = Client(HTTP_HOST=host)
    if not pages:
        print(("❌ " if strict_pages else "⚠️  ") + "No live public Wagtail pages found.")
        return int(strict_pages)

    print(f"🔎 Checking {len(pages)} live public Wagtail page(s) for host {host}...")
    for page in pages:
        path = page_path(page, wagtail_site)
        if not path:
            print(f"⚠️  Skipping page without URL: id={page.id} title={page.title!r}")
            continue
        response = client.get(path, follow=False)
        if response.status_code >= 400:
            print(f"❌ {path} -> HTTP {response.status_code} ({page.title})")
            failures += 1
            continue
        print(f"✅ {path} -> HTTP {response.status_code} ({page.title})")
        if response.status_code == 200 and strict_content:
            body = response.content.decode(response.charset or "utf-8", errors="ignore")
            if page.title and page.title not in body:
                print(f"❌ Page title not found in response body for {path}: {page.title!r}")
                failures += 1
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=os.getenv("DJANGO_SITE") or os.getenv("DJANGO_WEBSITE") or os.getenv("WEBSITE") or "ctc-research.com")
    parser.add_argument("--strict-assets", action="store_true", help="Fail if collected assets or webpack stats are missing.")
    parser.add_argument("--no-strict-content", action="store_true", help="Do not require each 200 response to contain its page title.")
    parser.add_argument("--strict-pages", action="store_true", help="Fail if Wagtail is unavailable or no live public pages exist.")
    args = parser.parse_args()

    configure(args.site)

    import django

    django.setup()
    failures = 0
    failures += check_assets(args.strict_assets)
    failures += check_pages(not args.no_strict_content, args.strict_pages)
    if failures:
        print(f"❌ Runtime verification failed with {failures} issue(s).")
        return 1
    print("✅ Runtime verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
