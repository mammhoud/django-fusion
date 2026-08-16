#!/usr/bin/env python3
"""Entry point for the precis-landing backend.

Allows execution via the canonical dispatcher, e.g.:
    cd projects && make check WEBSITE=precis-landing
    cd projects && uv run python precis/precis-landing/backend/__main__.py runserver
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    base_dir = Path(__file__).resolve().parent

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    os.environ.setdefault("DJANGO_SITE", "precis-landing")
    os.environ.setdefault("DJANGO_WEBSITE", "precis-landing")
    os.environ.setdefault("WEBSITE", "precis-landing")
    os.environ.setdefault("WEBSITE_NAME", "precis-landing")
    os.environ.setdefault("PROJECT_PATH", "precis-landing")

    # Ensure the backend root and the apps/ package are importable.
    for path in (str(base_dir), str(base_dir / "apps")):
        if path not in sys.path:
            sys.path.insert(0, path)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
