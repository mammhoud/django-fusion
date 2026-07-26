#!/usr/bin/env python3
"""Project-local wrapper for the unified workspace manage.py."""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

SITE = "cms-full"


def main() -> None:
    workspace = Path(__file__).resolve().parents[2]
    os.environ.setdefault("DJANGO_SITE", SITE)
    os.environ.setdefault("DJANGO_WEBSITE", SITE)
    os.environ.setdefault("WEBSITE", SITE)
    if not any(arg == "--site" or arg.startswith("--site=") for arg in sys.argv[1:]):
        sys.argv.insert(1, f"--site={SITE}")
    runpy.run_path(str(workspace / "manage.py"), run_name="__main__")


if __name__ == "__main__":
    main()
