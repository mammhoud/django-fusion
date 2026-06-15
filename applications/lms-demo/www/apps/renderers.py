"""
Renderer utilities for structa.cloud.

Delegates to django_osoul.handlers.core.DynamicComponentRenderer
"""

from django_osoul.handlers.core import DynamicComponentRenderer

# Singleton instance for easy access
dynamic_renderer = DynamicComponentRenderer()
