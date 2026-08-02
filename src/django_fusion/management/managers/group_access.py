"""
GroupAccessControl
==================
Static helpers for group-based access control.

Canonical import: from django_fusion.management.managers.group_access import GroupAccessControl

Pure Django — no Wagtail, no Celery.

Usage::

    from django_fusion.management.managers.group_access import GroupAccessControl

    if GroupAccessControl.check_group_access(request.user, ["editors", "admins"]):
        ...

    qs = GroupAccessControl.filter_by_group(Article.objects.all(), request.user)
"""

from __future__ import annotations

from typing import List

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()


class GroupAccessControl:
    """Static helpers for group-based access control."""

    @staticmethod
    def check_group_access(user: "User", required_groups: List[str]) -> bool:
        """Return ``True`` if *user* belongs to any of *required_groups*.

        Superusers always pass.
        """
        if user.is_superuser:
            return True
        user_groups = set(user.groups.values_list("name", flat=True))
        return bool(user_groups & set(required_groups))

    @staticmethod
    def check_role_access(user: "User", required_role: str) -> bool:
        """Return ``True`` if *user* belongs to the group named *required_role*.

        Superusers always pass.
        """
        if user.is_superuser:
            return True
        return user.groups.filter(name=required_role).exists()

    @staticmethod
    def get_accessible_groups(user: "User") -> List[Group]:
        """Return all groups the user belongs to (all groups for superusers)."""
        if user.is_superuser:
            return list(Group.objects.all())
        return list(user.groups.all())

    @staticmethod
    def filter_by_group(queryset, user: "User", group_field: str = "groups"):
        """Filter *queryset* to rows whose *group_field* overlaps the user's groups.

        Superusers receive the unfiltered queryset.
        """
        if user.is_superuser:
            return queryset
        user_groups = user.groups.all()
        return queryset.filter(**{f"{group_field}__in": user_groups}).distinct()
