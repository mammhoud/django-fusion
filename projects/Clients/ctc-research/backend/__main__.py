#!/usr/bin/env python3
"""Entry point for precis-lms website.

Allows execution via: python -m fusion_cms or uv run -m fusion_cms
"""
import os
import sys
from pathlib import Path

# Set site environment variables
os.environ.setdefault("DJANGO_SITE", "precis-lms")
os.environ.setdefault("DJANGO_WEBSITE", "precis-lms")
os.environ.setdefault("WEBSITE", "precis-lms")
os.environ.setdefault("WEBSITE_NAME", "precis-lms")
os.environ.setdefault("PROJECT_PATH", "precis-lms")
os.environ["MODULE"] = "LMS"

# Ensure workspace root is in path
workspace_root = Path(__file__).resolve().parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

# Ensure website directory is in path
site_dir = Path(__file__).resolve().parent
if str(site_dir) not in sys.path:
    sys.path.insert(0, str(site_dir))

# Ensure www directory is in path
www_dir = site_dir / "www"
if str(www_dir) not in sys.path:
    sys.path.insert(0, str(www_dir))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
