#!/usr/bin/env python3
"""Project-local manage.py for ctc-research.

Bootstraps Django directly with the correct PYTHONPATH for configs/ and the
local www/ app directory. Delegation via runpy.run_path() caused a pathlib
recursion issue, so this stays self-contained. The workspace manage.py at
websites/manage.py is available as a standalone multi-site dispatcher.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    site_dir = Path(__file__).resolve().parent          # websites/ctc-research/
    workspace_dir = site_dir.parent                     # websites/
    repo_root = site_dir.parents[2]                     # /home/structa.cloud/
    site_app_dir = site_dir / "www"                     # websites/ctc-research/www/

    # Set up Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    os.environ.setdefault("DJANGO_SITE", "ctc-research")
    os.environ.setdefault("DJANGO_WEBSITE", "ctc-research")
    os.environ.setdefault("WEBSITE", "ctc-research")

    # Build PYTHONPATH matching settings.py + Makefile workspace convention
    libs_dirs = [
        repo_root / "libs" / "django-fusion" / "src",
        repo_root / "libs" / "ceptor-ai" / "src",
    ]
    paths = [
        str(site_app_dir),
        str(site_dir),
        str(workspace_dir),
        str(repo_root / "projects"),
    ] + [str(p) for p in libs_dirs]
    for p in paths:
        if p not in sys.path:
            sys.path.insert(0, p)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
