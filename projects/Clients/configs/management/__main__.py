#!/usr/bin/env python3
"""Per-site entry point for the shared sentinel site.

Lets `python projects/tools/__main__.py <command>` route through the
existing `cli.py:SiteCLI` infrastructure.

The `tools` package (renamed from `projects/www/`) provides the shared
worker and CI infrastructure used across all websites. It serves as the
sentinel site for the shared-task worker stack (shared-worker +
shared-scheduler). The sentinel site is named `www` in the CLI config;
python code refers to it via `SiteCLI("www")` which resolves through
SITE_ALIASES to the `shared` site.

Usage examples from inside `projects/tools/`:
    python __main__.py check
    python __main__.py manage migrate
    python __main__.py shell
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # projects/

# The sentinel site is named "www" in the CLI config (SITES/SITE_ALIASES);
# SiteCLI("www") resolves through aliases to the "shared" site.
# The directory was renamed to `tools/` but the config name remains "www".
sys.path.insert(0, str(REPO_ROOT))

from cli import SiteCLI


def _main() -> None:
    args = sys.argv[1:]
    if not args:
        print(
            "Usage: python __main__.py <command> [args...]\n"
            "Commands: check, manage, migrate, shell, …\n"
            "Any Django management command is also available."
        )
        sys.exit(0)

    cmd, rest = args[0], args[1:]

    # Special direct-mapping command
    if cmd == "check":
        ok = SiteCLI("www").local_check()
        sys.exit(0 if ok else 1)

    # All other commands fan out to Django management
    cli = SiteCLI("www")
    cli.run_django_command([sys.argv[0], cmd, *rest])


if __name__ == "__main__":
    _main()
