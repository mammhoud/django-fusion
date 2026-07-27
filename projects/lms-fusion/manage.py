#!/usr/bin/env python3
"""Django's command-line utility for lms-fusion.

Examples:
  python manage.py migrate
  python manage.py check
  python manage.py runserver
"""

import sys
from pathlib import Path

# Add the site root to sys.path so we can import the local cli
SITE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE_ROOT))

from cli import SiteCLI


def main() -> None:
    cli = SiteCLI()
    cli.run_django_command(sys.argv)


if __name__ == "__main__":
    main()
