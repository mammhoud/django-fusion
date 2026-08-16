"""Tenant-aware auth adapters — identity layer for schema-per-tenant Cloud.

One adapter serves every tenant: the *adapter* is tenant-aware, not the
auth tables. Django auth lives in the shared ``public`` schema (global user
records), while every adapter decision reads the active tenant from the
django-tenants ``connection.tenant`` to return tenant-specific behaviour.

Import-safe on the SQLite dev default: django-allauth is optional here, so
``DefaultAccountAdapter`` is imported lazily and the base falls back to
``object`` when allauth is absent. With no active tenant (SQLite or public
schema) every decision returns the global default.
"""

from __future__ import annotations

from django.db import connection

try:  # pragma: no cover — allauth is optional in formint-cloud
    from allauth.account.adapter import DefaultAccountAdapter
except ImportError:  # pragma: no cover
    DefaultAccountAdapter = object


def active_tenant():
    """The django-tenants resolved tenant, or ``None`` outside a tenant."""
    return getattr(connection, "tenant", None)


class TenantAwareAccountAdapter(DefaultAccountAdapter):
    """One adapter, tenant-aware behaviour via the active schema."""

    def is_open_for_signup(self, request):
        # Per-tenant signup gate: allow per-branch/tenant setting.
        tenant = active_tenant()
        if tenant is None:
            return True  # public schema → admin/backoffice signup
        return bool((tenant.settings or {}).get("allow_signup", True))

    def get_login_redirect_url(self, request):
        # Branch-specific landing after login (POS desk vs backoffice).
        tenant = active_tenant()
        if tenant is not None:
            branch = tenant.default_branch
            if branch is not None:
                redirect = (branch.branch_settings.settings or {}).get(
                    "login_redirect"
                )
                if redirect:
                    return redirect
        if DefaultAccountAdapter is object:
            return "/"
        return super().get_login_redirect_url(request)
