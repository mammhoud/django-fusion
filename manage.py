#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks.

This manage.py supports switching between multiple website instances placed
under the `websites/` directory. Use the `--site` option or the
`DJANGO_SITE`/`SITE` environment variable to select which site's
`configs.settings` module will be used.

Examples:
  python manage.py --site=ctc-research.com migrate
  SITE=VResume python manage.py runserver
"""

import os
import sys
from pathlib import Path

# Map short names to actual site directory names (if you want aliases).
ALIASES = {
    "ctc": "ctc-research.com",
    "ctc-research": "ctc-research.com",
    "vresume": "VResume",
    "vresume": "VResume",
}


def _pop_site_arg(argv):
    """Pop a `--site` argument from argv and return its value.

    Supported forms: `--site=NAME` or `--site NAME`.
    If found, the arg (and its value) are removed from `argv` so Django
    receives the remaining args normally.
    """
    for idx, a in enumerate(argv[1:], start=1):
        if a.startswith("--site="):
            val = a.split("=", 1)[1]
            del argv[idx]
            return val
        if a == "--site" and idx + 1 < len(argv):
            val = argv[idx + 1]
            del argv[idx: idx + 2]
            return val
    return None


def main():
    # Allow CLI arg to override env vars.
    site_arg = _pop_site_arg(sys.argv) or os.environ.get("DJANGO_SITE") or os.environ.get("SITE")
    if site_arg:
        selected = ALIASES.get(site_arg.lower(), site_arg)
    else:
        # sensible default when nothing is provided
        selected = "ctc-research.com"

    base_dir = Path(__file__).resolve().parent  # websites/
    site_dir = base_dir / selected

    if site_dir.exists():
        # Ensure the repo root and selected site directory are on sys.path so
        # `import configs` will resolve to the chosen site's `configs` package.
        repo_root = str(base_dir.parent)
        site_path = str(site_dir)
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        if site_path not in sys.path:
            sys.path.insert(0, site_path)
        print(f"Using site '{selected}' (site path: {site_path})", file=sys.stderr)
    else:
        print(f"Warning: site directory '{site_dir}' not found; continuing with current PYTHONPATH", file=sys.stderr)

    # If the environment hasn't provided a settings module, use the site's
    # `configs.settings` by default (the site directory was just pushed onto
    # `sys.path`, so `configs` will resolve from the chosen site).
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
