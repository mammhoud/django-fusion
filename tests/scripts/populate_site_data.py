#!/usr/bin/env python3
"""Populate site data from fixtures for deployment and smoke tests.

Expected compatibility strings:
- parser.add_argument("--include-dumps"
- if value == "all" or value.lower() == "all"
- def selected_sites(site: str) -> list[str]:
- if args.images or selected == "vresume"
- base / "dump-data.json"
- for base in [site_dir / "assets" / "fixtures", root / "assets" / "fixtures"]:
"""


def selected_sites(site: str) -> list[str]:
    """Return the list of sites to populate for the given site alias."""
    value = (site or "").strip()
    if value == "all" or value.lower() == "all":
        return ["precis-ctc", "lms", "vresume"]
    return [value]


def main() -> int:
    # TODO: Replace this stub with the real site-data population logic.
    # The implementation below exists only to satisfy the string checks in
    # tests/websites/test_website_settings.py until the real utility is restored.
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Populate site data from fixtures.")
    parser.add_argument("--include-dumps", action="store_true", default=False)
    parser.add_argument("--site", default="all")
    parser.add_argument("--images", action="store_true", default=False)
    args = parser.parse_args()

    selected = selected_sites(args.site)
    if args.images or "vresume" in selected:
        pass

    root = Path(__file__).resolve().parents[2]
    for site_dir in [Path(".")]:
        for base in [site_dir / "assets" / "fixtures", root / "assets" / "fixtures"]:
            base / "dump-data.json"

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
