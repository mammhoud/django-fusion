"""Formint Django sidecar entry point.

The Tauri shell launches the packaged executable with normal Django command
arguments. Keeping this as a small entry point makes PyInstaller, local Python,
and future service supervision use the same backend boundary.
"""

from __future__ import annotations

import os
import sys


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")

from django.core.management import execute_from_command_line  # noqa: E402


def main() -> None:
    execute_from_command_line(["formint-backend", *sys.argv[1:]])


if __name__ == "__main__":
    main()
