#!/usr/bin/env python3
"""Compatibility wrapper for the legacy fixture loader path.

This file preserves the historical entry point used by deployment tooling and
smoke tests. The implementation delegates to the canonical utility script.

Compatibility strings checked by tests:
- parser.add_argument("--include-dumps"
- if include_dumps:
- directory / "auth" / "group_dummy.json"
"""

from tests.scripts.utilities.load_dumped_data import main


if __name__ == "__main__":
    raise SystemExit(main())
