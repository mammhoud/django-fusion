"""Runtime helpers for shared tasks that can execute for any website."""

from __future__ import annotations

import importlib
import os
import sys
from typing import Any


def configure_django_for_website(website: str | None = None) -> str:
    """Configure environment and initialize Django for the selected website."""
    site_module = importlib.import_module("configs.site")
    selected = site_module.active_website_name(
        website
        or os.getenv("DJANGO_SITE")
        or os.getenv("DJANGO_WEBSITE")
        or os.getenv("WEBSITE")
        or "ctc-research.com"
    )
    site_module.configure_site_environment(selected)
    for path in (site_module.site_dir_for(selected), site_module.WORKSPACE_DIR):
        path_text = str(path)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    django_module = importlib.import_module("django")
    apps_module = importlib.import_module("django.apps")
    if not apps_module.apps.ready:
        django_module.setup()
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
