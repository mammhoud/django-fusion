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

    def available_apps(self, apps: Iterable[str]) -> list[str]:
        return [
            app
            for app in apps
            if self.module_exists(self.optional_map.get(app, app))
        ]

    @staticmethod
    def merge(*app_groups: Iterable[str]) -> list[str]:
        merged: list[str] = []
        for group in app_groups:
            merged.extend(group)
        return merged
