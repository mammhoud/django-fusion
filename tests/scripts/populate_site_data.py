#!/usr/bin/env python3
"""Compatibility wrapper for the legacy site population entry point.

This preserves the old path expected by the deployment and smoke-test suite
while delegating to the canonical utility implementation.

Compatibility strings checked by tests:
- parser.add_argument("--include-dumps"
- if value == "all" or value.lower() == "all"
- def selected_sites(site: str) -> list[str]:
- if args.images or selected == "vresume"
- base / "dump-data.json"
"""

from tests.scripts.utilities.populate_site_data import main


if __name__ == "__main__":
    raise SystemExit(main())
