#!/usr/bin/env python3
"""
Django's command-line utility with multi-site support and DevOps commands.

This file is the main entry point for both Django management commands and
the extended utility commands (deploy, logs, push, etc.).

Examples:
  python manage.py --site=lms-demo migrate
  python manage.py sites
  python manage.py deploy ctc-research --no-cache
  python manage.py validate-commands
  python manage.py make-check --all
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add the repository root to sys.path
REPO_ROOT = Path(__file__).resolve().parent
ROOT_COMPOSE = REPO_ROOT / "docker-compose.yml"

# Import SiteCLI from cli module
from cli import SiteCLI

# Mapping of utility command names to SiteCLI methods
UTILITY_COMMANDS = {
    "sites": "sites",
    "make": "make",
    "make-check": "make_check",
    "check-sites": "check_sites",
    "local-check": "local_check",
    "deploy": "deploy",
    "logs": "logs",
    "down": "down",
    "ps": "ps",
    "build-assets": "build_assets",
    "test": "test",
    "push": "push",
    "validate-commands": "validate_commands",
}


def main() -> None:
    # Support old --list-sites flag (maps to 'sites' command)
    if "--list-sites" in sys.argv:
        sys.argv.remove("--list-sites")
        cli = SiteCLI()
        sys.exit(cli.sites([]))

    # If the first argument is a utility command, dispatch it
    if len(sys.argv) > 1 and sys.argv[1] in UTILITY_COMMANDS:
        cmd_name = sys.argv[1]
        # Extract site from --site argument if present
        site_arg = SiteCLI.pop_site_arg(sys.argv)
        site = SiteCLI.resolve_site(site_arg) if site_arg else None
        cli = SiteCLI(site)
        method = getattr(cli, UTILITY_COMMANDS[cmd_name])
        sys.exit(method(sys.argv[2:]))

    # Otherwise, treat as Django command
    site_arg = SiteCLI.pop_site_arg(sys.argv)
    site = SiteCLI.resolve_site(site_arg) if site_arg else None
    cli = SiteCLI(site)
    cli.run_django_command(sys.argv)


if __name__ == "__main__":
    main()
