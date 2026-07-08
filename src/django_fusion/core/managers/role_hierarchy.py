"""
RoleHierarchyManager
====================
Manages role hierarchy and permission inheritance for Django groups.

Canonical import: from django_fusion.core.managers import RoleHierarchyManager

Pure Django — no Wagtail, no Celery.

Usage::

    class MyRoleManager(RoleHierarchyManager):
        ROLE_HIERARCHY = {
            "admin": ["supervisor", "user"],
            "supervisor": ["user"],
            "user": [],
        }
        ROLE_PERMISSIONS = {
            "admin": ["auth.add_user", "auth.change_user"],
            "supervisor": ["auth.view_user"],
            "user": [],
        }

    mgr = MyRoleManager()
    perms = mgr.get_all_permissions_for_role("admin")
    hierarchy = mgr.get_role_hierarchy("supervisor")
"""

from __future__ import annotations

from typing import List, Set, Tuple

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class RoleHierarchyManager:
    """
    Manages role hierarchy and permission inheritance.

    Subclass and override ``ROLE_HIERARCHY`` and ``ROLE_PERMISSIONS`` as class
    attributes to define the role structure for a specific website.
    """

    # Override in subclass: parent roles inherit permissions from child roles
    ROLE_HIERARCHY: dict[str, list[str]] = {}

    # Override in subclass: direct permissions per role
    ROLE_PERMISSIONS: dict[str, list[str]] = {}

    def __init__(self) -> None:
        self._permission_cache: dict[str, set[str]] = {}

    # ------------------------------------------------------------------
    # Permission resolution
    # ------------------------------------------------------------------

    def get_all_permissions_for_role(self, role: str) -> Set[str]:
        """Return all permissions for *role*, including inherited ones.

        The result is cached per-instance so repeated calls are O(1).
        """
        if role in self._permission_cache:
            return self._permission_cache[role]

        permissions: set[str] = set(self.ROLE_PERMISSIONS.get(role, []))

        for child_role in self.ROLE_HIERARCHY.get(role, []):
            permissions.update(self.get_all_permissions_for_role(child_role))

        self._permission_cache[role] = permissions
        return permissions

    def get_role_hierarchy(self, role: str) -> List[str]:
        """Return the full hierarchy list starting with *role* itself."""
        hierarchy = [role]
        for child_role in self.ROLE_HIERARCHY.get(role, []):
            hierarchy.extend(self.get_role_hierarchy(child_role))
        return hierarchy

    # ------------------------------------------------------------------
    # Group management
    # ------------------------------------------------------------------

    @transaction.atomic
    def create_or_update_group(self, role: str) -> Tuple[Group, bool]:
        """Create or update a Django ``Group`` with the role's permissions."""
        group, created = Group.objects.get_or_create(name=role)

        permission_codenames = self.get_all_permissions_for_role(role)
        permissions = []
        for perm_string in permission_codenames:
            try:
                app_label, codename = perm_string.split(".")
                perm = Permission.objects.get(
                    content_type__app_label=app_label, codename=codename
                )
                permissions.append(perm)
            except (Permission.DoesNotExist, ValueError):
                pass

        group.permissions.set(permissions)
        return group, created

    # ------------------------------------------------------------------
    # User assignment
    # ------------------------------------------------------------------

    @transaction.atomic
    def assign_user_to_role(self, user: "User", role: str) -> bool:
        """Assign *user* to *role* and all roles in its hierarchy."""
        user.groups.clear()
        for r in self.get_role_hierarchy(role):
            group, _ = Group.objects.get_or_create(name=r)
            user.groups.add(group)
        return True

    @transaction.atomic
    def assign_user_to_multiple_roles(self, user: "User", roles: List[str]) -> bool:
        """Assign *user* to multiple roles (and their hierarchies)."""
        user.groups.clear()
        all_roles: set[str] = set()
        for role in roles:
            all_roles.update(self.get_role_hierarchy(role))
        for r in all_roles:
            group, _ = Group.objects.get_or_create(name=r)
            user.groups.add(group)
        return True

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_user_roles(self, user: "User") -> List[str]:
        """Return the list of group names (roles) the user belongs to."""
        return list(user.groups.values_list("name", flat=True))

    def get_user_permissions(self, user: "User") -> Set[str]:
        """Return all permissions the user has via groups and direct assignment."""
        permissions: set[str] = set()
        for group in user.groups.all():
            for perm in group.permissions.all():
                permissions.add(f"{perm.content_type.app_label}.{perm.codename}")
        for perm in user.user_permissions.all():
            permissions.add(f"{perm.content_type.app_label}.{perm.codename}")
        return permissions

    def has_role(self, user: "User", role: str) -> bool:
        """Return ``True`` if *user* belongs to the group named *role*."""
        return user.groups.filter(name=role).exists()

    def has_permission(self, user: "User", permission: str) -> bool:
        """Return ``True`` if *user* has *permission* (``"app.codename"`` format)."""
        if user.is_superuser:
            return True
        try:
            app_label, codename = permission.split(".")
            return user.has_perm(f"{app_label}.{codename}")
        except ValueError:
            return False
