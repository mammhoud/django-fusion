"""Reusable helpers for concise Django base setting modules."""

from __future__ import annotations

import importlib.util
from collections.abc import Iterable, Mapping


class AppRegistry:
    """Filter Django app lists using lightweight import availability checks."""

    def __init__(self, optional_map: Mapping[str, str] | None = None):
        self.optional_map = dict(optional_map or {})

    @staticmethod
    def module_exists(module_name: str) -> bool:
        try:
            return importlib.util.find_spec(module_name) is not None
        except ModuleNotFoundError:
            return False

    def has_any(self, *module_names: str) -> bool:
        return any(self.module_exists(module_name) for module_name in module_names)

    @staticmethod
    def _app_module(app: str) -> str:
        """
        Convert a Django app string to its importable module path.

        Django accepts two app-entry formats:
          1. A dotted module path:  "myapp.apps.MyConfig"   → check "myapp"
          2. A plain module path:   "myapp.subpackage"      → check as-is

        The heuristic: if the last component starts with an uppercase letter
        it is an AppConfig class name, so we drop it and check the parent module.
        """
        parts = app.split(".")
        if parts and parts[-1][0].isupper():
            # e.g. "www.core.content.apps.ContentConfig" → "www.core.content"
            # Remove the class name and the module that holds it (apps.py)
            # so we resolve to the package directory, not a submodule.
            candidate_parts = parts[:-1]
            if candidate_parts and candidate_parts[-1] in ("apps",):
                candidate_parts = candidate_parts[:-1]
            return ".".join(candidate_parts) if candidate_parts else app
        return app

    def available_apps(self, apps: Iterable[str]) -> list[str]:
        return [
            app
            for app in apps
            if self.module_exists(self.optional_map.get(app, self._app_module(app)))
        ]

    @staticmethod
    def merge(*app_groups: Iterable[str]) -> list[str]:
        merged: list[str] = []
        for group in app_groups:
            merged.extend(group)
        return merged
