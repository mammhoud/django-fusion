"""
Group and role management services for the handlers app.

Re-exports the shared RoleHierarchyManager from django-fusion with
the site-specific role hierarchy and permissions configured.
"""

from django.db import transaction
from django_fusion.core.managers import GroupAccessControl
from django_fusion.core.managers import RoleHierarchyManager as _BaseRoleHierarchyManager


class RoleHierarchyManager(_BaseRoleHierarchyManager):
    """
    Site-specific role hierarchy manager for fusion-cms.com.

    Defines the role hierarchy and permissions for the three standard roles:
    admin > supervisor > user
    """

    ROLE_HIERARCHY = {
        "admin": ["supervisor"],
        "supervisor": ["user"],
        "user": [],
    }

    ROLE_PERMISSIONS = {
        "admin": [
            "auth.add_user",
            "auth.change_user",
            "auth.delete_user",
            "auth.view_user",
        ],
        "supervisor": [
            "auth.change_user",
            "auth.view_user",
        ],
        "user": [
            "auth.view_user",
        ],
    }

    @transaction.atomic
    def assign_user_to_role(self, user, role: str) -> bool:
        """Assign user to role and all roles in its hierarchy, creating groups with permissions."""
        user.groups.clear()
        for r in self.get_role_hierarchy(role):
            group, _ = self.create_or_update_group(r)
            user.groups.add(group)
        return True

    @transaction.atomic
    def assign_user_to_multiple_roles(self, user, roles) -> bool:
        """Assign user to multiple roles (and their hierarchies), creating groups with permissions."""
        user.groups.clear()
        all_roles: set = set()
        for role in roles:
            all_roles.update(self.get_role_hierarchy(role))
        for r in all_roles:
            group, _ = self.create_or_update_group(r)
            user.groups.add(group)
        return True


__all__ = ["RoleHierarchyManager", "GroupAccessControl"]
