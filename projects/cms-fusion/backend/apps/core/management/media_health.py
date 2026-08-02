"""Backward-compatible CMS import for the shared media health check."""

from django_fusion.core.health.checks import media_health_check

__all__ = ["media_health_check"]
