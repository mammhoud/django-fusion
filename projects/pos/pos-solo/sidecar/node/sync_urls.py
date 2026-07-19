"""
Sync API URL configuration for Solo edition.
Provides endpoints for triggering sync, checking status, and viewing logs.

@tested pos-portal/solo - Sync URLs
"""

from __future__ import annotations

from django.urls import path

from . import sync_views

urlpatterns = [
    path("status/", sync_views.sync_status, name="sync-status"),
    path("trigger/", sync_views.trigger_sync, name="sync-trigger"),
    path("config/", sync_views.update_sync_config, name="sync-config"),
    path("log/", sync_views.sync_log, name="sync-log"),
]
