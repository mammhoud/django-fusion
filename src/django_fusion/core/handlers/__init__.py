"""
Handler classes and utilities for django_fusion.

This package contains pure Django handler classes, middleware, and utilities
that can be used across projects without Wagtail dependencies.
"""

from .base import ErrorTrackerMiddleware
from .emails import (
    DynamicComponentRenderer,
    EmailTemplateRegistry,
    EmailTemplateSelector,
    GroupAccessControl,
    RoleHierarchyManager,
)
from .mixins import ProfileContextMixin, ProfileDashboardMixin, ProfileOperationsMixin  # noqa

__all__ = [
    "ErrorTrackerMiddleware",
    "RoleHierarchyManager",
    "GroupAccessControl",
    "DynamicComponentRenderer",
    "EmailTemplateSelector",
    "EmailTemplateRegistry",
    "ProfileContextMixin",
    "ProfileDashboardMixin",
    "ProfileOperationsMixin",
]
