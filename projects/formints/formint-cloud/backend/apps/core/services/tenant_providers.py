"""Per-tenant provider settings — social/auth provider overrides with a
public-schema fallback.

Tenant-level ``settings`` JSON may carry ``{"social": {provider_id: {...}}}``
overrides. When a tenant is active its override wins; otherwise the global
``SOCIALACCOUNT_PROVIDERS`` settings value is returned.
"""

from __future__ import annotations

from django.conf import settings
from django.db import connection


def tenant_provider_settings(provider_id: str) -> dict:
    """Resolve per-tenant provider overrides, falling back to global settings."""
    tenant = getattr(connection, "tenant", None)
    if tenant is not None:
        overrides = (tenant.settings or {}).get("social", {}).get(provider_id, {})
        if overrides:
            return overrides
    return getattr(settings, "SOCIALACCOUNT_PROVIDERS", {}).get(provider_id, {})
