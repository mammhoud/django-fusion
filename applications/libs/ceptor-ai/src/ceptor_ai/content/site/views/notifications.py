"""
Notification views.

Re-exports from django_osoul.contrib.views.notifications for backward compatibility.

Canonical import: from django_osoul.contrib.views import NotificationView
"""

from django_osoul.site.views.notifications import NotificationView  # noqa: F401

__all__ = ["NotificationView"]
