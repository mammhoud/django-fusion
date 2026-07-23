"""Backward-compatibility re-exports for django_fusion.site.utils.

This module keeps old ``django_fusion.site.utils`` imports working by
forwarding them to the new canonical location under ``django_fusion.ci``.
It also hosts the small string utilities that used to live here and are
imported by ``django_fusion.contrib``.
"""
from __future__ import annotations

import re

# Re-export utilities that now live in django_fusion.ci.utils
from django_fusion.ci.utils import (  # noqa: F401
    bytes_to_mib,
    file_generate_name,
    file_generate_upload_path,
    get_default_language,
    get_files_from_dirs,
    get_root_redirect_pattern,
    unique_ordered,
    viewprop,
)

# Sentinel used by routing to mean "use the default value / not provided".
DEFAULT = object()


def camel_case_to_underscore(name: str) -> str:
    """Convert ``CamelCase`` to ``camel_case``.

    >>> camel_case_to_underscore("MyViewset")
    'my_viewset'
    """
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def strip_suffixes(name: str, suffixes: list[str]) -> str:
    """Remove the first matching suffix from ``name``.

    >>> strip_suffixes("MyViewset", ["Viewset", "App"])
    'My'
    """
    for suffix in suffixes:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def list_path_components(path: str) -> list[str]:
    """Split a URL path into non-empty components.

    >>> list_path_components("/a/b//c/")
    ['a', 'b', 'c']
    """
    return [part for part in path.split("/") if part]


__all__ = [
    "bytes_to_mib",
    "camel_case_to_underscore",
    "DEFAULT",
    "file_generate_name",
    "file_generate_upload_path",
    "get_default_language",
    "get_files_from_dirs",
    "get_root_redirect_pattern",
    "list_path_components",
    "strip_suffixes",
    "unique_ordered",
    "viewprop",
]
