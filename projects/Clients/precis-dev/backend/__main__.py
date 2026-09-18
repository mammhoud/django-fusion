#!/usr/bin/env python3
"""Entry point for the precis-main backend.

Allows execution via the canonical dispatcher, e.g.:
    cd projects && make check WEBSITE=precis-main
    cd projects && uv run python structa.cloud/backend/__main__.py runserver
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    base_dir = Path(__file__).resolve().parent

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    os.environ.setdefault("DJANGO_SITE", "precis-main")
    os.environ.setdefault("DJANGO_WEBSITE", "precis-main")
    os.environ.setdefault("WEBSITE", "precis-main")
    os.environ.setdefault("WEBSITE_NAME", "precis-main")
    os.environ.setdefault("PROJECT_PATH", "precis-main")

    # Ensure the backend root and the apps/ package are importable.
    for path in (str(base_dir), str(base_dir / "apps")):
        if path not in sys.path:
            sys.path.insert(0, path)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
