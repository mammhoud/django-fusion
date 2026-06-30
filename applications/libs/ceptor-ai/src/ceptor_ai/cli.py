"""Command-line helpers for the local ceptor-ai package."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .components import extract_components_from_file, write_component_files
from .projects import project_package_uses
from .rseal import migration_plan


def package_info() -> dict[str, str | bool]:
    """Return metadata used by Kilo commands and package checks."""
    return {
        "name": "ceptor-ai",
        "import_package": "ceptor_ai",
        "standalone": True,
        "mcp_module": "ceptor_ai.mcp_server:app",
        "rseal_migration": True,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the ceptor-ai command parser."""
    parser = argparse.ArgumentParser(prog="ceptor-ai")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("info", help="Print package metadata as JSON.")
    subparsers.add_parser("health", help="Run a lightweight package health check.")
    subparsers.add_parser("projects", help="Print website package usage as JSON.")
    rseal_parser = subparsers.add_parser(
        "rseal-plan",
        help="Print a ceptor-ai import migration plan as JSON.",
    )
    rseal_parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Project root to scan for ceptor_ai imports.",
    )
    extract_parser = subparsers.add_parser(
        "extract-components",
        help="Extract low-depth HTML components for theme/Ollama indexing tasks.",
    )
    extract_parser.add_argument("html_file", help="HTML file to inspect.")
    extract_parser.add_argument("--max-depth", type=int, default=2)
    extract_parser.add_argument("--output-dir", help="Write each component HTML snippet to this directory.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ceptor-ai CLI."""
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

    if args.command == "extract-components":
        components = extract_components_from_file(args.html_file, max_depth=args.max_depth)
        payload = [component.as_dict() for component in components]
        if args.output_dir:
            written = write_component_files(components, args.output_dir)
            for item, path in zip(payload, written):
                item["output_file"] = str(path)
        print(json.dumps(payload, sort_keys=True))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2
