"""Runtime helpers for shared tasks that can execute for any website.

Provides two key functions used by all Dramatiq and Celery actors
in ``www.worker``:

1. :func:`configure_django_for_website` — Configures Django's
   environment (``DJANGO_SETTINGS_MODULE``, ``sys.path``) for a
   specific tenant website before executing a task. This is what
   allows the shared-worker to process tasks for any site without
   impersonating that site at the process level.

2. :func:`import_first` — Tries importing from a list of dotted
   paths and returns the first successful result. Used to resolve
   email service implementations that may live in different modules
   across sites (plugins vs www.apps vs www.core).

Typical usage in an actor::

    from .runtime import configure_django_for_website, import_first

    @dramatiq.actor
    def my_task(website=None):
        configure_django_for_website(website)
        service = import_first(["my.module.Service"])
        service().run()
"""

from __future__ import annotations

import importlib
import os
import sys
from typing import Any


def configure_django_for_website(website: str | None = None) -> str:
    """Configure environment and initialize Django for the selected website.

    Resolves the website name (from argument, env vars, or default),
    calls ``configure_site_environment()`` to seed the process env,
    and adds the website and workspace directories to ``sys.path``
    so Django can discover the site's ``settings`` module.

    This is safe to call multiple times — subsequent calls for the
    same website are idempotent.

    Args:
        website: Optional website slug (e.g. ``"fusion-cms"``).
            Falls back to ``DJANGO_SITE``, ``DJANGO_WEBSITE``,
            ``WEBSITE`` env vars, or ``"fusion-cms.com"``.

    Returns:
        The canonical website name that was configured (may differ
        from the input if an alias was resolved).
    """
    site_module = importlib.import_module("configs.site")
    selected = site_module.active_website_name(
        website
        or os.getenv("DJANGO_SITE")
        or os.getenv("DJANGO_WEBSITE")
        or os.getenv("WEBSITE")
        or "fusion-cms.com"
    )
    site_module.configure_site_environment(selected)
    for path in (site_module.site_dir_for(selected), site_module.WORKSPACE_DIR):
        path_text = str(path)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    # rundramatiq already sets up Django; avoid redundant setup here.
    return selected


def import_first(import_paths: list[str]) -> Any:
    """Import the first available dotted object path."""
    last_missing: str | None = None
    for import_path in import_paths:
        module_path, _, attr = import_path.rpartition(".")
        if importlib.util.find_spec(module_path) is None:
            last_missing = module_path
            continue
        module = importlib.import_module(module_path)
        if hasattr(module, attr):
            return getattr(module, attr)
        last_missing = import_path
    raise ImportError(f"No import path available from: {last_missing or import_paths}")
