"""Compatibility shim — ``ceptor_ai.components`` is now ``ceptor_ai.content.extraction``.

Import from the canonical path instead::

    from ceptor_ai.content.extraction import extract_components_from_html
    from ceptor_ai.content.extraction import ExtractedComponent
"""
from __future__ import annotations
from ceptor_ai.content.extraction import (  # noqa: F401
    ExtractedComponent,
    extract_components_from_file,
    extract_components_from_html,
    write_component_files,
)

__all__ = [
    "ExtractedComponent",
    "extract_components_from_file",
    "extract_components_from_html",
    "write_component_files",
]
