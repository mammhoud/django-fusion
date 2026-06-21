"""Command-line helpers for the local crafts-ai package."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence


def package_info() -> dict[str, str | bool]:
    """Return metadata used by Kilo commands and package checks."""
    return {
        "name": "crafts-ai",
        "import_package": "crafts_ai",
        "standalone": True,
        "mcp_module": "crafts_ai.mcp_server:app",
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the crafts-ai command parser."""
    parser = argparse.ArgumentParser(prog="crafts-ai")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("info", help="Print package metadata as JSON.")
    subparsers.add_parser("health", help="Run a lightweight package health check.")
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

    parser.error(f"unknown command: {args.command}")
    return 2
