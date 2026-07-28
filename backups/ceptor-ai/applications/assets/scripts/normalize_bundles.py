#!/usr/bin/env python3
"""Post-processor: normalise webpack bundles.json string chunks to dicts.

webpack-bundle-tracker v3+ writes chunks as plain strings like::

    {"app": ["runtime-abc123.js", ...]}

django-webpack-loader v3.2.3 expects dict chunks with 'name'/'url' keys::

    {"app": [{"name": "runtime-abc123.js", "url": "bundles/site/runtime-abc123.js"}]}

This script reads bundles.json and converts string chunks to dict form
so {% render_bundle %} works without runtime monkey-patching.

Usage:
    python normalize_bundles.py <bundles.json> [--bundle-dir bundles/vresume/]
"""

import argparse
import json
import sys
from pathlib import Path


def normalize(stats: dict, bundle_dir: str) -> dict:
    """Convert string chunks to dict chunks in-place."""
    chunks = stats.get("chunks")
    if not isinstance(chunks, dict):
        return stats
    for bundle_name, entries in chunks.items():
        if not entries:
            continue
        chunks[bundle_name] = [
            {"name": c, "url": f"{bundle_dir}{c}", "path": c}
            if isinstance(c, str) else c
            for c in entries
        ]
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalise bundles.json string chunks to dicts")
    parser.add_argument("bundles_json", type=Path, help="Path to bundles.json")
    parser.add_argument(
        "--bundle-dir",
        default="",
        help="Bundle directory prefix for URLs (e.g. 'bundles/vresume/')",
    )
    args = parser.parse_args()

    path: Path = args.bundles_json
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        stats = json.load(f)

    # Determine bundle_dir from publicPath if not explicitly provided
    bundle_dir = args.bundle_dir or ""
    if not bundle_dir and isinstance(stats.get("publicPath"), str):
        # publicPath is like "/static/bundles/vresume/"
        public_path: str = stats["publicPath"]
        bundle_dir = public_path.lstrip("/")

    stats = normalize(stats, bundle_dir)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=None, separators=(",", ":"))
    print(f"OK: Normalised {path} (bundle_dir={bundle_dir!r})")


if __name__ == "__main__":
    main()
