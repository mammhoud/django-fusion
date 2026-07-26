"""
Renderer utilities for structa.cloud.

Delegates to django_fusion.handlers.core.DynamicComponentRenderer
"""

from django_fusion.core.handlers.emails import DynamicComponentRenderer

# Singleton instance for easy access
dynamic_renderer = DynamicComponentRenderer()
