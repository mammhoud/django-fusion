"""Backward-compatible CMS import for the shared asset health check."""

from django_fusion.core.health.checks import asset_health_check

__all__ = ["asset_health_check"]
