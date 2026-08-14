#!/usr/bin/env python3
"""Loop-CRM backend management entry point (mirrors landing-fusion conventions)."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    base_dir = Path(__file__).resolve().parent

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    os.environ.setdefault("DJANGO_SITE", "loop-crm")
    os.environ.setdefault("WEBSITE", "loop-crm")
    os.environ.setdefault("WEBSITE_NAME", "loop-crm")

    # Ensure the backend root and the apps/ package are importable.
    for path in (str(base_dir), str(base_dir / "apps")):
        if path not in sys.path:
            sys.path.insert(0, path)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
