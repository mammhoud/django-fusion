"""Command-line helpers for the local crafts-ai package."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .projects import project_package_uses
from .rseal import migration_plan


def package_info() -> dict[str, str | bool]:
    """Return metadata used by Kilo commands and package checks."""
    return {
        "name": "crafts-ai",
        "import_package": "crafts_ai",
        "standalone": True,
        "mcp_module": "crafts_ai.mcp_server:app",
        "rseal_migration": True,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the crafts-ai command parser."""
    parser = argparse.ArgumentParser(prog="crafts-ai")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("info", help="Print package metadata as JSON.")
    subparsers.add_parser("health", help="Run a lightweight package health check.")
    subparsers.add_parser("projects", help="Print website package usage as JSON.")
    rseal_parser = subparsers.add_parser(
        "rseal-plan",
        help="Print a django-rseal import migration plan as JSON.",
    )
    rseal_parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Project root to scan for django_rseal imports.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the crafts-ai CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in {None, "info"}:
        print(json.dumps(package_info(), sort_keys=True))
        return 0

    if args.command == "health":
        print(json.dumps({"status": "ok", **package_info()}, sort_keys=True))
        return 0

    if args.command == "projects":
        payload = [item.__dict__ for item in project_package_uses()]
        print(json.dumps(payload, sort_keys=True))
        return 0

    if args.command == "rseal-plan":
        payload = [item.as_dict() for item in migration_plan(Path(args.root))]
        print(json.dumps(payload, sort_keys=True))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2
