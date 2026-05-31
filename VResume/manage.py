#!/usr/bin/env python
"""Django's command-line utility for vResume within the workspace."""
import os
import sys
from pathlib import Path


def main():
    site_dir = Path(__file__).resolve().parent
    workspace_dir = site_dir.parent
    site_app_dir = site_dir / "www"
    for path in (site_app_dir, site_dir, workspace_dir):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)

    os.environ.setdefault("DJANGO_WEBSITE", "vresume")
    os.environ.setdefault("WEBSITE", "vresume")
    os.environ.setdefault("WEBSITE_NAME", "vresume")
    os.environ.setdefault("DJANGO_WEBSITE_DIR", str(site_dir))
    os.environ.setdefault("WEBSITE_DIR", str(site_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
