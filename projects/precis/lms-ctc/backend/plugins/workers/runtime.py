"""Runtime helpers for site-neutral Dramatiq workers."""

from __future__ import annotations

import importlib
import os
import sys
from typing import Any


def configure_django_for_website(website: str | None = None) -> str:
    """Prepare Django import paths for the selected registered website."""
    site_module = importlib.import_module("configs.site")
    selected = site_module.active_website_name(
        website
        or os.getenv("DJANGO_SITE")
        or os.getenv("DJANGO_WEBSITE")
        or os.getenv("WEBSITE")
        or "shared"
    )
    site_module.configure_site_environment(selected)
    for path in (
        site_module.site_dir_for(selected),
        getattr(site_module, "PROJECT_DIR", None),
        site_module.WORKSPACE_DIR,
    ):
        if path is None:
            continue
        path_text = str(path)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    return selected


def import_first(import_paths: list[str]) -> Any:
    """Import and return the first available dotted object path."""
    last_missing: str | None = None
    for import_path in import_paths:
        module_path, _, attr = import_path.rpartition(".")
        try:
            module = importlib.import_module(module_path)
        except ImportError:
            last_missing = module_path
            continue
        if hasattr(module, attr):
            return getattr(module, attr)
        last_missing = import_path
    raise ImportError(f"No import path available from: {last_missing or import_paths}")
