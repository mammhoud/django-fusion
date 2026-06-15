#!/usr/bin/env python3
"""Populate a workspace site with JSON fixtures and optional image/content data.

This script gives all websites the same entry point for test/demo data:

1. Run migrations for the selected site.
2. Load JSON fixtures from the site's ``assets/fixtures`` directory and the
   shared ``tests/fixtures`` directory when present.
3. Optionally run the VResume Python populator, which creates Wagtail image
   objects and rich page/snippet content from source/static images or generated
   placeholders.

It is intentionally conservative: missing optional fixture directories are
reported and skipped so the command works for all three sites.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

SITE_ALIASES = {
    "ctc": "ctc-research",
    "ctc-research": "ctc-research",
    "ctc-research.com": "ctc-research",
    "structa": "lms-demo",
    "lms": "lms-demo",
    "lms-demo": "lms-demo",
    "structa.cloud": "lms-demo",
    "vresume": "vresume",
    "VResume": "vresume",
    "resume": "vresume",
}
SITE_DIRS = {
    "ctc-research": "ctc-research",
    "lms-demo": "lms-demo",
    "vresume": "VResume",
}


def normalize_site(value: str) -> str:
    if value == "all" or value.lower() == "all":
        return "all"
    return SITE_ALIASES.get(value, SITE_ALIASES.get(value.lower(), value))


def selected_sites(site: str) -> list[str]:
    return list(SITE_DIRS) if site == "all" else [site]


def python_bin(root: Path) -> str:
    candidate = root / ".venv" / "bin" / "python"
    return str(candidate) if candidate.exists() else sys.executable


def run(cmd: list[str], root: Path, site: str, dry_run: bool = False) -> int:
    env = os.environ.copy()
    env.update({"DJANGO_SITE": site, "DJANGO_WEBSITE": site, "WEBSITE": site, "PROJECT_PATH": site})
    print("$", " ".join(cmd))
    if dry_run:
        return 0
    return subprocess.run(cmd, cwd=root, env=env, check=False).returncode


def fixture_candidates(root: Path, site: str, include_shared: bool, include_dumps: bool) -> list[Path]:
    site_dir = root / SITE_DIRS.get(site, site)
    candidates: list[Path] = []
    for base in [site_dir / "assets" / "fixtures", root / "assets" / "fixtures"]:
        if not base.exists():
            print(f"Skipping missing fixture directory: {base.relative_to(root)}")
            continue
        preferred = [
            base / "auth" / "group_dummy.json",
            base / "auth" / "user_dummy.json",
            base / "sites" / "site_dummy.json",
            base / "initial_choices.json",
            base / "users.json",
        ]
        if include_dumps:
            preferred.extend([base / "dump-data.json", base / "wagtail_pages_dump.json"])
            preferred.extend(sorted(base.glob("*dump*.json")))
        for path in preferred:
            if path.exists() and path not in candidates:
                candidates.append(path)
    if include_shared:
        for path in [root / "tests" / "fixtures" / "models_fixture.json", root / "tests" / "fixtures" / "dumped_data_fixture.json"]:
            if path.exists() and path not in candidates:
                candidates.append(path)
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=os.getenv("DJANGO_SITE") or "ctc-research")
    parser.add_argument("--skip-migrate", action="store_true", help="Do not run migrations before loading fixtures.")
    parser.add_argument("--skip-json", action="store_true", help="Do not load JSON fixtures.")
    parser.add_argument("--include-shared", action="store_true", help="Also load shared tests/fixtures JSON files.")
    parser.add_argument("--include-dumps", action="store_true", help="Also load legacy dump/page JSON fixtures with hard-coded Wagtail/contenttype IDs.")
    parser.add_argument("--images", action="store_true", help="Run site-specific Python image/content population when available.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them.")
    parser.add_argument("extra", nargs="*", help="Extra arguments passed to the site-specific Python populator.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    site = normalize_site(args.site)
    py = python_bin(root)

    for selected in selected_sites(site):
        if not args.skip_migrate:
            rc = run([py, "manage.py", f"--site={selected}", "migrate", "--noinput"], root, selected, args.dry_run)
            if rc != 0:
                return rc

        if not args.skip_json:
            # Use the unified data populator that handles duplicate permissions and homepage fixing
            rc = run([py, "tests/scripts/utilities/load_dumped_data.py", "--site", selected, "--include-dumps" if args.include_dumps else "--force"], root, selected, args.dry_run)
            if rc != 0:
                return rc

        if args.images or selected == "vresume":
            if selected == "vresume":
                rc = run([py, "-m", "configs.tests.data_populator", "--verbose", *args.extra], root, selected, args.dry_run)
                if rc != 0:
                    return rc
            else:
                print(f"No Python image/content populator registered for {selected}; JSON fixtures loaded only.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
