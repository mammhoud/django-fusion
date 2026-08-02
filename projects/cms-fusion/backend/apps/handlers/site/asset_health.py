"""Backward-compatible CMS handler import for asset health."""

from django_fusion.core.health.checks import asset_health_check

__all__ = ["asset_health_check"]
