#!/usr/bin/env python3
"""
Django dev server startup — sets up correct PYTHONPATH before running.
Resolves the www.core conflict between projects/www and projects/lms/cms/www.
"""
import os
import sys
from pathlib import Path

# ── Locate directories ──────────────────────────────────────────────
this_file = Path(__file__).resolve()
cms_dir = this_file.parent                      # projects/lms/cms/
workspace_dir = cms_dir.parent                  # projects/lms/
repo_root = workspace_dir.parents[1]             # structa.cloud/ (actual repo root)
projects_dir = repo_root / "projects"            # structa.cloud/projects/

# ── Set environment ────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ.setdefault("DJANGO_SITE", "lms")
os.environ.setdefault("DJANGO_WEBSITE", "lms")
os.environ.setdefault("WEBSITE", "lms")
os.environ["DJANGO_PRINT_ENV"] = "false"

# ── Build PYTHONPATH (priority order) ──────────────────────────────
# CMS www/ must come BEFORE projects/ so that 'www.core' resolves to
# projects/lms/cms/www/core, NOT projects/www/core (which lacks core).
paths = [
    str(cms_dir / "www"),                        # cms/www — site-specific www
    str(cms_dir),                                # cms/     — site root
    str(workspace_dir),                          # lms/     — workspace
    str(projects_dir),                           # projects/ — shared apps
    str(repo_root),                              # repo root
    str(repo_root / "libs" / "django-fusion" / "src"),
    str(repo_root / "libs" / "ceptor-ai" / "src"),
    str(repo_root / "libs" / "django-bolt" / "python"),
]

for p in reversed(paths):
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Run server ──────────────────────────────────────────────────────
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
