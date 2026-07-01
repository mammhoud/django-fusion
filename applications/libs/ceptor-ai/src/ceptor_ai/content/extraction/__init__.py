"""HTML component extraction utilities.

Parses rendered HTML pages to identify reusable component candidates
(low-depth ``div`` containers with associated assets). Used by offline
indexing, CLI commands, and the Ollama integration.

Usage::

    from ceptor_ai.content.extraction import extract_components_from_html
    from ceptor_ai.content.extraction import extract_components_from_file
    from ceptor_ai.content.extraction import write_component_files
    from ceptor_ai.content.extraction import ExtractedComponent
"""

from .extractor import (
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
