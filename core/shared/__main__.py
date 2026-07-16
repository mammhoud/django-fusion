#!/usr/bin/env python3
"""Per-site entry point for the `shared` sentinel site.

Lets `python core/shared/__main__.py <command>` route through the
existing `cli.py:SiteCLI` infrastructure exactly the way per-site
`__main__.py` does for ctc-research / lms-demo / VResume.

Usage examples from inside `core/shared/`:
    python __main__.py check
    python __main__.py manage migrate
    python __main__.py shell
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # core/

# Per-site `__main__.py` reads `cwd = Path(__file__).resolve().parent`
# and uses the directory name as the default site key. For shared,
# `parent.name = "shared"` so the parent lookup falls through to the
# alias resolution; SITE_ALIASES carries both `shared` and
# `shared-worker`/`shared-scheduler` mappings. Calling `SiteCLI("shared")`
# explicitly here is more defensive than the cwd-sniff approach used by
# per-site `__main__.py` because shared-worker / shared-scheduler may be
# invoked from any cwd inside the container.
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
        ok = SiteCLI("shared").local_check()
        sys.exit(0 if ok else 1)

    # All other commands fan out to Django management
    cli = SiteCLI("shared")
    cli.run_django_command([sys.argv[0], cmd, *rest])


if __name__ == "__main__":
    _main()
