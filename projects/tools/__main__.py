#!/usr/bin/env python3
"""Per-site entry point for the merged `www` sentinel site.

Lets `python projects/www/__main__.py <command>` route through the
existing `cli.py:SiteCLI` infrastructure exactly the way per-site
`__main__.py` does for ctc-research / lms / VResume.

The `www` site (created from the merge of `projects/shared/` and
`projects/www/`) provides the shared/core Django application code
used across all websites. It serves as the sentinel site for the
shared-task worker stack (shared-worker + shared-scheduler).

Usage examples from inside `projects/www/`:
    python __main__.py check
    python __main__.py manage migrate
    python __main__.py shell
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # projects/

# Per-site `__main__.py` reads `cwd = Path(__file__).resolve().parent`
# and uses the directory name as the default site key. For www,
# `parent.name = "www"` so the alias resolution carries both `www` and
# `shared-worker`/`shared-scheduler` mappings. Calling `SiteCLI("www")`
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
        ok = SiteCLI("www").local_check()
        sys.exit(0 if ok else 1)

    # All other commands fan out to Django management
    cli = SiteCLI("www")
    cli.run_django_command([sys.argv[0], cmd, *rest])


if __name__ == "__main__":
    _main()
