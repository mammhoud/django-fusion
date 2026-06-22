"""
Template management for django_osoul components.

Modules:
- templates: Template handling and utilities
"""

from .templates import *  # noqa: F401, F403

__all__ = []

from .discovery import discover_sections

__all__.append("discover_sections")
