#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks.

This manage.py supports switching between multiple site directories in this
workspace. Use the `--site` option or the `DJANGO_SITE`/`SITE` environment
variable to select which site's settings module will be used.

Examples:
  python manage.py --site=ctc-research migrate
  SITE=lms-demo python manage.py runserver
"""

import os
import sys
from pathlib import Path

# Map short names to actual site directory names.
ALIASES = {
    "ctc": "ctc-research",
    "ctc-research": "ctc-research",
    "ctc-research.com": "ctc-research",
    "structa": "lms-demo",
    "structa.cloud": "lms-demo",
    "core": "lms-demo",
    "lms": "lms-demo",
    "lms-demo": "lms-demo",
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
        selected = "ctc-research"

    repo_root = Path(__file__).resolve().parent
    source_dir = repo_root / selected
    wrapper_dir = repo_root / "websites" / selected
    site_dir = source_dir if source_dir.exists() else wrapper_dir

    if site_dir.exists():
        # Ensure the repo root and selected site directory are on sys.path. The
        # repo root exposes shared configs; the site directory exposes website
        # apps, templates, static assets, and website-local settings.py.
        for path in (str(site_dir), str(repo_root)):
            if path not in sys.path:
                sys.path.insert(0, path)
        os.environ.setdefault("DJANGO_WEBSITE", selected)
        os.environ.setdefault("WEBSITE", selected)
        os.environ.setdefault("WEBSITE_NAME", selected)
        os.environ.setdefault("DJANGO_WEBSITE_DIR", str(site_dir))
        os.environ.setdefault("WEBSITE_DIR", str(site_dir))
        print(f"Using site '{selected}' (site path: {site_dir})", file=sys.stderr)
    else:
        print(f"Warning: site directory '{site_dir}' not found; continuing with current PYTHONPATH", file=sys.stderr)

    # Prefer website-local settings.py; wrapper configs/settings.py remains
    # available for deployments that explicitly use configs.settings.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

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
