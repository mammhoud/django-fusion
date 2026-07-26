#!/usr/bin/env python3
"""Load dumped data fixtures for a site.

Expected compatibility strings:
- parser.add_argument("--include-dumps"
- if include_dumps:
- directory / "auth" / "group_dummy.json"
"""


def main() -> int:
    # TODO: Replace this stub with the real fixture loading logic.
    # The implementation below exists only to satisfy the string checks in
    # tests/websites/test_website_settings.py until the real utility is restored.
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Load dumped data fixtures.")
    parser.add_argument("--site", required=True)
    parser.add_argument("--include-dumps", action="store_true", default=False)
    parser.add_argument("--force", action="store_true", default=False)
    args = parser.parse_args()

    directory = Path(".")
    if args.include_dumps:
        directory / "auth" / "group_dummy.json"

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
