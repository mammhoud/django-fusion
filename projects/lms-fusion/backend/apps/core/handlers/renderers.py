"""
Renderer utilities for ctc-research.com.

Delegates to django_fusion.handlers.core.DynamicComponentRenderer
"""

from django_fusion.core.handlers import DynamicComponentRenderer

# Singleton instance for easy access
dynamic_renderer = DynamicComponentRenderer()
