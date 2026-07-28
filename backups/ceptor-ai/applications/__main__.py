#!/usr/bin/env python3
"""
Per‑site entry point for running Django commands and checks.

This file should be placed inside each site folder (e.g., lms-demo/__main__.py).
It auto‑detects the site based on the directory name and delegates all
commands to the central SiteCLI.

Usage examples (from inside the site folder):
  python __main__.py check
  python __main__.py manage migrate
  python __main__.py shell
"""

import os
import sys
from pathlib import Path

# Add the repository root to sys.path so we can import cli
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from cli import SiteCLI


def main() -> None:
    # Determine the site name from the directory containing this __main__.py
    site_dir = Path(__file__).resolve().parent
    site_name = site_dir.name

    # Map VResume to vresume if needed (canonical name in SITES)
    if site_name == "VResume":
        site_name = "vresume"

    # Verify that the site exists in configuration
    if site_name not in SiteCLI.resolve_site.__closure__[0].cell_contents:
        # Fallback: use SITE_ALIASES lookup
        try:
            site_name = SiteCLI.resolve_site(site_name)
        except SystemExit:
            print(f"Unknown site directory: {site_dir.name}", file=sys.stderr)
            sys.exit(1)

    cli = SiteCLI(site_name)

    args = sys.argv[1:]
    if not args:
        print("Usage: python __main__.py <command> [args...]")
        print("Commands: check, manage, migrate, shell, test, ...")
        print("Any Django management command is also available.")
        sys.exit(0)

    cmd, rest = args[0], args[1:]

    # Special commands that map directly to SiteCLI methods
    if cmd == "check":
        # Run local __main__.py check (re‑entrant, but safe)
        ok = cli.local_check()
        sys.exit(0 if ok else 1)
    elif cmd == "manage":
        # Delegate to Django management command
        cli.run_django_command([sys.argv[0], *rest])
    else:
        # For all other commands, run as Django management command
        # (migrate, shell, test, collectstatic, etc.)
        cli.run_django_command([sys.argv[0], cmd, *rest])


if __name__ == "__main__":
    main()
