"""
Renderer utilities for fusion-cms.com.

Uses django-fusion's canonical dynamic component renderer.
"""

from django_fusion.management.handlers.emails import DynamicComponentRenderer

# Singleton instance for easy access
dynamic_renderer = DynamicComponentRenderer()
