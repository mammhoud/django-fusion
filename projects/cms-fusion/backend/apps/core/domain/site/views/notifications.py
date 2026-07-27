"""
Notification views.

Re-exports from django_fusion.contrib.views.notifications for backward compatibility.

Canonical import: from django_fusion.contrib.views import NotificationView
"""

from django_fusion.site.interface.views.notifications import NotificationView  # noqa: F401

__all__ = ["NotificationView"]
