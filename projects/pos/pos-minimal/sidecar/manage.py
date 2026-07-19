#!/usr/bin/env python3
"""Django management entry point for minimal POS Portal.

@tested pos-portal/minimal - Manage.py entry point
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    os.environ.setdefault("WEBSITE", "minimal-portal")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
