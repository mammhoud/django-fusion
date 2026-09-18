"""Tenant context processor — exposes ``current_tenant`` and its branch
settings to every template/API view without a second lookup.

Returns ``None`` for both when no tenant is resolved (SQLite dev default or
the public schema), so templates can branch on ``current_tenant`` safely.
"""

from __future__ import annotations


def tenant(request):
    from django.db import connection

    tenant = getattr(connection, "tenant", None)
    branch_settings = None
    if tenant is not None:
        branch = tenant.default_branch
        if branch is not None:
            branch_settings = branch.branch_settings
    return {
        "current_tenant": tenant,
        "branch_settings": branch_settings,
    }
