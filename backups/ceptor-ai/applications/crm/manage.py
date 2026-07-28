#!/usr/bin/env python
"""Django management script for the CRM site."""
import sys
import os
from pathlib import Path

_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent

for _path in (str(_SITE_DIR / "www"), str(_SITE_DIR), str(_WORKSPACE_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
