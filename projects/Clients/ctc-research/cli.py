#!/usr/bin/env python3
"""Minimal standalone CLI for precis-lms.

This is a self-contained entry point that configures Django and runs
management commands. It does NOT depend on projects/cli.py.
"""

import os
import sys
from pathlib import Path


class SiteCLI:
    """Minimal site controller for precis-lms."""

    SITE_NAME = "precis-lms"

    def __init__(self, site: str | None = None) -> None:
        self.site_name = site or self.SITE_NAME
        self.site_dir = Path(__file__).resolve().parent
        self.workspace_root = self.site_dir.parent  # projects/
        self.backend_dir = self.site_dir / "backend"

    def configure_django(self) -> None:
        """Set up sys.path and environment for Django."""
        # Add paths to sys.path (site root, backend, and backend/www).
        # Important: DO NOT add projects/ (workspace_root) — it would cause
        # Django test discovery to scan precis-lms/ as a package, leading to
        # "doesn't declare an explicit app_label" errors.
        for path in [
            str(self.site_dir),
            str(self.backend_dir),
            str(self.backend_dir / "www"),
        ]:
            if path not in sys.path:
                sys.path.insert(0, path)

        # Set Django environment
        os.environ.setdefault("DJANGO_SITE", self.SITE_NAME)
        os.environ.setdefault("DJANGO_WEBSITE", self.SITE_NAME)
        os.environ.setdefault("WEBSITE", self.SITE_NAME)
        os.environ.setdefault("WEBSITE_NAME", self.SITE_NAME)
        os.environ.setdefault("PROJECT_PATH", self.SITE_NAME)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    def run_django_command(self, argv: list[str]) -> None:
        """Configure and execute a Django management command."""
        self.configure_django()
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable?"
            ) from exc
        execute_from_command_line(argv)


if __name__ == "__main__":
    cli = SiteCLI()
    print(f"Site: {cli.site_name}")
