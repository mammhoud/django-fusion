#!/usr/bin/env python3
"""Project-local management entry point for precis-lms."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    site_dir = Path(__file__).resolve().parent
    project_dir = site_dir.parent

    os.environ.setdefault("DJANGO_SITE", "precis-lms")
    os.environ.setdefault("DJANGO_WEBSITE", "precis-lms")
    os.environ.setdefault("WEBSITE", "precis-lms")
    os.environ.setdefault("WEBSITE_NAME", "precis-lms")
    os.environ.setdefault("PROJECT_PATH", "precis-lms")
    os.environ.setdefault("MODULE", "FUSION")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    # Ensure project and workspace roots are importable.
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))
    workspace_root = project_dir.parent
    if str(workspace_root) not in sys.path:
        sys.path.insert(0, str(workspace_root))
    www_dir = site_dir / "www"
    if str(www_dir) not in sys.path:
        sys.path.insert(0, str(www_dir))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
