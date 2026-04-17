"""
Service module for Wagtail group and role management.

Provides high-level operations for managing groups, roles, and permissions.
"""

from typing import List, Optional

from django.contrib.auth.models import Group, User
from django.db import transaction

from core.CI.models.group import GroupContentAccess, RoleEmailMapping, WagtailGroupRole


class GroupManagementService:
    """Service for managing Wagtail groups and roles."""

    @staticmethod
    def create_group_with_role(
        group_name: str,
        role_type: str,
        description: str = '',
        parent_role: Optional[WagtailGroupRole] = None
    ) -> WagtailGroupRole:
        """
        Create a new group with role configuration.

        Args:
            group_name: Name of the group
            role_type: Type of role (from WagtailGroupRole.RoleType)
            description: Description of the group
            parent_role: Parent role for permission inheritance

        Returns:
            Created WagtailGroupRole instance
        """
        with transaction.atomic():
            group, _ = Group.objects.get_or_create(name=group_name)

            role, created = WagtailGroupRole.objects.get_or_create(
                group=group,
                defaults={
                    'role_type': role_type,
                    'description': description,
                    'parent_role': parent_role,
                }
            )

            if parent_role:
                role.sync_permissions_from_parent()

            return role

    @staticmethod
    def assign_user_to_group(user: User, group: Group) -> bool:
        """
        Assign a user to a group.

        Args:
            user: User object
            group: Group object

        Returns:
            Boolean indicating success
        """
        if group not in user.groups.all():
            user.groups.add(group)
            return True
        return False

    @staticmethod
    def remove_user_from_group(user: User, group: Group) -> bool:
        """
        Remove a user from a group.

        Args:
            user: User object
            group: Group object

        Returns:
            Boolean indicating success
        """
        if group in user.groups.all():
            user.groups.remove(group)
            return True
        return False

    @staticmethod
    def sync_user_email_roles(user: User, email_roles: List[str]) -> int:
        """
        Synchronize user's groups based on email roles.

        Args:
            user: User object
            email_roles: List of email role identifiers

        Returns:
            Number of groups assigned
        """
        groups = []

        for email_role in email_roles:
            group = RoleEmailMapping.get_group_for_email_role(email_role)
            if group:
                groups.append(group)

        user.groups.set(groups)
        return len(groups)

    @staticmethod
    def grant_content_access(
        group: Group,
        content_type: str,
        access_level: str,
        content_id: str = ''
    ) -> GroupContentAccess:
        """
        Grant content access to a group.

        Args:
            group: Group object
            content_type: Content type identifier
            access_level: Access level (view, edit, publish, admin)
            content_id: Specific content ID (optional)

        Returns:
            GroupContentAccess instance
        """
        access, _ = GroupContentAccess.objects.get_or_create(
            group=group,
            content_type=content_type,
            content_id=content_id,
            defaults={'access_level': access_level}
        )

        if access.access_level != access_level:
            access.access_level = access_level
            access.save()

        return access

    @staticmethod
    def revoke_content_access(
        group: Group,
        content_type: str,
        content_id: str = ''
    ) -> bool:
        """
        Revoke content access from a group.

        Args:
            group: Group object
            content_type: Content type identifier
            content_id: Specific content ID (optional)

        Returns:
            Boolean indicating if access was revoked
        """
        deleted, _ = GroupContentAccess.objects.filter(
            group=group,
            content_type=content_type,
            content_id=content_id
        ).delete()

        return deleted > 0

    @staticmethod
    def check_user_content_access(
        user: User,
        content_type: str,
        access_level: str = 'view',
        content_id: str = ''
    ) -> bool:
        """
        Check if user has access to content.

        Args:
            user: User object
            content_type: Content type identifier
            access_level: Required access level
            content_id: Specific content ID (optional)

        Returns:
            Boolean indicating if user has access
        """
        user_groups = user.groups.all()

        for group in user_groups:
            if GroupContentAccess.has_access(
                group,
                content_type,
                access_level,
                content_id
            ):
                return True

        return False

    @staticmethod
    def get_user_accessible_content(
        user: User,
        content_type: str,
        access_level: str = 'view'
    ) -> List[str]:
        """
        Get all content IDs accessible to a user.

        Args:
            user: User object
            content_type: Content type identifier
            access_level: Required access level

        Returns:
            List of accessible content IDs
        """
        accessible_content = set()

        for group in user.groups.all():
            content_ids = GroupContentAccess.get_user_accessible_content(
                user,
                content_type,
                access_level
            )
            accessible_content.update(content_ids)

        return list(accessible_content)

    @staticmethod
    def check_user_role_level(user: User, required_role_type: str) -> bool:
        """
        Check if user has required role level or higher.

        Args:
            user: User object
            required_role_type: Required role type

        Returns:
            Boolean indicating if user has required role level
        """
        return WagtailGroupRole.has_permission_level(user, required_role_type)

    @staticmethod
    def get_user_highest_role(user: User) -> Optional[str]:
        """
        Get the highest role type for a user.

        Args:
            user: User object

        Returns:
            Highest role type or None
        """
        user_roles = WagtailGroupRole.objects.filter(
            group__user=user,
            is_active=True
        ).values_list('role_type', flat=True)

        if not user_roles:
            return None

        highest = max(
            user_roles,
            key=lambda r: WagtailGroupRole.get_role_hierarchy_level(r)
        )

        return highest

    @staticmethod
    def create_email_role_mapping(
        email_role: str,
        group: Group,
        description: str = ''
    ) -> RoleEmailMapping:
        """
        Create a mapping between email role and Wagtail group.

        Args:
            email_role: Email role identifier
            group: Wagtail group
            description: Description of the mapping

        Returns:
            RoleEmailMapping instance
        """
        mapping, _ = RoleEmailMapping.objects.get_or_create(
            email_role=email_role,
            defaults={
                'wagtail_group': group,
                'description': description,
            }
        )

        return mapping

    @staticmethod
    def deactivate_group(group: Group) -> bool:
        """
        Deactivate a group.

        Args:
            group: Group object

        Returns:
            Boolean indicating success
        """
        try:
            role = WagtailGroupRole.objects.get(group=group)
            role.is_active = False
            role.save()
            return True
        except WagtailGroupRole.DoesNotExist:
            return False

    @staticmethod
    def activate_group(group: Group) -> bool:
        """
        Activate a group.

        Args:
            group: Group object

        Returns:
            Boolean indicating success
        """
        try:
            role = WagtailGroupRole.objects.get(group=group)
            role.is_active = True
            role.save()
            return True
        except WagtailGroupRole.DoesNotExist:
            return False
