"""Framework-agnostic component extraction helpers."""

from .extractor import ExtractedComponent, extract_components_from_file, extract_components_from_html, write_component_files

__all__ = [
    "ExtractedComponent",
    "extract_components_from_file",
    "extract_components_from_html",
    "write_component_files",
]
