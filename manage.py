#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Add libs directory to Python path for local packages
    project_root = Path(__file__).parent.parent
    libs_path = project_root / "libs"

    # Add each package in libs to Python path
    for package_dir in libs_path.glob("*/"):
        if package_dir.is_dir() and (package_dir / "src").exists():
            sys.path.insert(0, str(package_dir / "src"))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
