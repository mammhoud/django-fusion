"""
Renderer utilities for ctc-research.com.

Delegates to django_osoul.handlers.core.DynamicComponentRenderer
"""

from django_osoul.core.handlers.core import DynamicComponentRenderer

# Singleton instance for easy access
dynamic_renderer = DynamicComponentRenderer()
