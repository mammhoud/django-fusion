#!/usr/bin/env python3
"""Per‑site entry point for running Django commands and checks.

Usage examples (from inside the site folder):
  python __main__.py check
  python __main__.py manage migrate
  python __main__.py shell
"""

import sys
from pathlib import Path

# Add the site root to sys.path so we can import the local cli
SITE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE_ROOT))

from cli import SiteCLI


def main() -> None:
    cli = SiteCLI()

    args = sys.argv[1:]
    if not args:
        print("Usage: python __main__.py <command> [args...]")
        print("Commands: check, manage, migrate, shell, test, ...")
        print("Any Django management command is also available.")
        sys.exit(0)

    cmd, rest = args[0], args[1:]

    # Special commands that map directly to SiteCLI methods
    if cmd == "manage":
        # Delegate to Django management command
        cli.run_django_command([sys.argv[0], *rest])
    else:
        # For all other commands, run as Django management command
        # (migrate, shell, test, collectstatic, etc.)
        cli.run_django_command([sys.argv[0], cmd, *rest])


if __name__ == "__main__":
    main()
