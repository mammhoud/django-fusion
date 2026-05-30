#!/usr/bin/env python3
"""
Entry point for lms-demo website CLI.
Usage:
  python lms-demo/__main__.py check
  python lms-demo/__main__.py manage migrate
  python lms-demo/__main__.py shell
"""
import os
import subprocess
import sys
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
MANAGE = SITE_DIR / "manage.py"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
sys.path.insert(0, str(SITE_DIR))


def _run_manage(*args):
    result = subprocess.run([sys.executable, str(MANAGE), *args])
    sys.exit(result.returncode)


COMMANDS = {
    "check":           lambda a: _run_manage("check", *a),
    "migrate":         lambda a: _run_manage("migrate", *a),
    "makemigrations":  lambda a: _run_manage("makemigrations", *a),
    "collectstatic":   lambda a: _run_manage("collectstatic", *a),
    "shell":           lambda a: _run_manage("shell", *a),
    "test":            lambda a: _run_manage("test", *a),
    "manage":          lambda a: _run_manage(*a),
}


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python __main__.py <command> [args...]")
        print(f"Commands: {', '.join(COMMANDS)}")
        sys.exit(0)
    cmd, rest = args[0], args[1:]
    if cmd not in COMMANDS:
        # fall through to manage.py directly
        _run_manage(cmd, *rest)
    else:
        COMMANDS[cmd](rest)


if __name__ == "__main__":
    main()
