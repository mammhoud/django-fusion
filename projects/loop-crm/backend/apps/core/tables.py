"""Tenant-safe django-tables2 tables for Loop-CRM workspace screens."""
from __future__ import annotations

import django_tables2 as tables
from django.contrib.auth import get_user_model

from .permissions import is_marketing, is_revops, is_sales, role_of


class MemberTable(tables.Table):
    """Member directory: identity, live role, workspace, and capabilities only."""

    username = tables.Column(verbose_name="Member")
    email = tables.EmailColumn(verbose_name="Email")
    role = tables.Column(verbose_name="Role")
    workspace = tables.Column(verbose_name="Workspace", empty_values=())
    permissions = tables.Column(verbose_name="Access", empty_values=())
    status = tables.Column(verbose_name="Status", empty_values=())

    class Meta:
        model = get_user_model()
        fields = ("username", "email")
        attrs = {
            "class": "loop-table",
            "thead": {"class": "loop-table__head"},
            "tbody": {"class": "loop-table__body"},
        }
        empty_text = "No workspace members yet."

    def render_username(self, value, record):
        return record.get_full_name() or value or record.email

    def render_role(self, value, record):
        return role_of(record).replace("_", " ").title()

    def render_workspace(self, value, record):
        profile = getattr(record, "profile", None)
        return getattr(getattr(profile, "workspace", None), "name", "Unassigned")

    def render_permissions(self, value, record):
        permissions = []
        if is_sales(record):
            permissions.append("sales")
        if is_marketing(record):
            permissions.append("marketing")
        if is_revops(record):
            permissions.append("revops")
        return ", ".join(permissions) or "view"

    def render_status(self, value, record):
        return "Active" if record.is_active else "Inactive"
