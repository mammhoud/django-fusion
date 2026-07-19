"""
Sync Proxy URL configuration for Solo edition compatibility.

@tested pos-portal/full/cloud - Sync URLs
"""

from __future__ import annotations

from django.urls import path

from . import sync_proxy

urlpatterns = [
    path("status/", sync_proxy.sync_status, name="sync-status"),
    path("push/<str:entity_type>/", sync_proxy.push_entity, name="sync-push"),
    path("bulk-push/<str:entity_type>/", sync_proxy.bulk_push_entities, name="sync-bulk-push"),
]
