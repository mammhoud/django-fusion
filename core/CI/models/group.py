"""
Wagtail group and role management models.

Provides models for managing Wagtail groups with role-based permission inheritance
and group-based content access control.
"""

from django.contrib.auth.models import Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class WagtailGroupRole(models.Model):
    """
    Extended Wagtail group with role hierarchy and permission inheritance.

    Manages role-based permission inheritance and group-based content access control.
    """

    class RoleType(models.TextChoices):
        ADMIN = 'admin', _('Administrator')
        SUPERVISOR = 'supervisor', _('Supervisor')
        MANAGER = 'manager', _('Manager')
        EDITOR = 'editor', _('Editor')
        CONTRIBUTOR = 'contributor', _('Contributor')
        VIEWER = 'viewer', _('Viewer')

    # Role hierarchy (higher number = higher privilege)
    ROLE_HIERARCHY = {
        RoleType.ADMIN: 6,
        RoleType.SUPERVISOR: 5,
        RoleType.MANAGER: 4,
        RoleType.EDITOR: 3,
        RoleType.CONTRIBUTOR: 2,
        RoleType.VIEWER: 1,
    }

    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='wagtail_role',
        help_text=_('Django group associated with this role')
    )
    role_type = models.CharField(
        max_length=50,
        choices=RoleType.choices,
        db_index=True,
        help_text=_('Role type in the hierarchy')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Description of the group role and responsibilities')
    )
    parent_role = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_roles',
        help_text=_('Parent role in the hierarchy (for permission inheritance)')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_('Whether this group is active and can be assigned to users')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wagtail_group_role'
        unique_together = [['group', 'role_type']]
        ordering = ['-role_type']
        verbose_name = _('Wagtail Group Role')
        verbose_name_plural = _('Wagtail Group Roles')

    def __str__(self):
        return f"{self.group.name} ({self.get_role_type_display()})"

    def get_inherited_permissions(self):
        """
        Get all permissions for this role including inherited permissions.

        Returns:
            QuerySet of Permission objects
        """
        permissions = set(self.group.permissions.all())

        # Add inherited permissions from parent role
        if self.parent_role:
            parent_perms = self.parent_role.get_inherited_permissions()
            permissions.update(parent_perms)

        return permissions

    def sync_permissions_from_parent(self):
        """
        Synchronize permissions from parent role.

        Adds all parent role permissions to this group.
        """
        if self.parent_role:
            parent_perms = self.parent_role.get_inherited_permissions()
            self.group.permissions.add(*parent_perms)

    @classmethod
    def get_role_hierarchy_level(cls, role_type):
        """
        Get the hierarchy level for a role type.

        Args:
            role_type: The role type string

        Returns:
            Integer representing the hierarchy level
        """
        return cls.ROLE_HIERARCHY.get(role_type, 0)

    @classmethod
    def has_permission_level(cls, user, required_role_type):
        """
        Check if user has required role level or higher.

        Args:
            user: User object
            required_role_type: Required role type string

        Returns:
            Boolean indicating if user has required permission level
        """
        user_roles = cls.objects.filter(
            group__user=user,
            is_active=True
        ).values_list('role_type', flat=True)

        if not user_roles:
            return False

        user_highest_level = max(
            cls.get_role_hierarchy_level(role) for role in user_roles
        )
        required_level = cls.get_role_hierarchy_level(required_role_type)

        return user_highest_level >= required_level


class GroupContentAccess(models.Model):
    """
    Manages group-based content access control.

    Defines which groups can access specific content types and pages.
    """

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='content_access',
        help_text=_('Group with access to content')
    )
    content_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text=_('Content type identifier (e.g., "page", "blog", "document")')
    )
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('view', _('View Only')),
            ('edit', _('Edit')),
            ('publish', _('Publish')),
            ('admin', _('Admin')),
        ],
        default='view',
        help_text=_('Level of access granted to this group')
    )
    content_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text=_('Specific content ID (leave blank for all content of this type)')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'group_content_access'
        unique_together = [['group', 'content_type', 'content_id']]
        ordering = ['content_type', 'group']
        verbose_name = _('Group Content Access')
        verbose_name_plural = _('Group Content Access')

    def __str__(self):
        content_desc = f" - {self.content_id}" if self.content_id else ""
        return f"{self.group.name} ({self.get_access_level_display()}) {self.content_type}{content_desc}"

    @classmethod
    def has_access(cls, group, content_type, access_level='view', content_id=None):
        """
        Check if a group has access to specific content.

        Args:
            group: Group object
            content_type: Content type identifier
            access_level: Required access level
            content_id: Specific content ID (optional)

        Returns:
            Boolean indicating if group has access
        """
        access_levels = {
            'view': ['view', 'edit', 'publish', 'admin'],
            'edit': ['edit', 'publish', 'admin'],
            'publish': ['publish', 'admin'],
            'admin': ['admin'],
        }

        required_levels = access_levels.get(access_level, [access_level])

        # Check for specific content access
        if content_id:
            access = cls.objects.filter(
                group=group,
                content_type=content_type,
                content_id=content_id,
                access_level__in=required_levels
            ).exists()
            if access:
                return True

        # Check for general content type access
        access = cls.objects.filter(
            group=group,
            content_type=content_type,
            content_id='',
            access_level__in=required_levels
        ).exists()

        return access

    @classmethod
    def get_user_accessible_content(cls, user, content_type, access_level='view'):
        """
        Get all content IDs accessible to a user for a specific content type.

        Args:
            user: User object
            content_type: Content type identifier
            access_level: Required access level

        Returns:
            List of content IDs accessible to the user
        """
        access_levels = {
            'view': ['view', 'edit', 'publish', 'admin'],
            'edit': ['edit', 'publish', 'admin'],
            'publish': ['publish', 'admin'],
            'admin': ['admin'],
        }

        required_levels = access_levels.get(access_level, [access_level])

        # Get all groups for the user
        user_groups = user.groups.all()

        # Get all accessible content
        accessible = cls.objects.filter(
            group__in=user_groups,
            content_type=content_type,
            access_level__in=required_levels
        ).values_list('content_id', flat=True).distinct()

        return list(accessible)


class RoleEmailMapping(models.Model):
    """
    Maps email roles to Wagtail groups for synchronization.

    Enables automatic synchronization between email role system and Wagtail groups.
    """

    email_role = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_('Email role identifier (e.g., "admin", "supervisor")')
    )
    wagtail_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='email_role_mappings',
        help_text=_('Wagtail group to map to this email role')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Description of the email role mapping')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_('Whether this mapping is active')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'role_email_mapping'
        ordering = ['email_role']
        verbose_name = _('Role Email Mapping')
        verbose_name_plural = _('Role Email Mappings')

    def __str__(self):
        return f"{self.email_role} → {self.wagtail_group.name}"

    @classmethod
    def get_group_for_email_role(cls, email_role):
        """
        Get the Wagtail group for an email role.

        Args:
            email_role: Email role identifier

        Returns:
            Group object or None
        """
        mapping = cls.objects.filter(
            email_role=email_role,
            is_active=True
        ).first()

        return mapping.wagtail_group if mapping else None

    @classmethod
    def sync_user_groups_from_email_roles(cls, user, email_roles):
        """
        Synchronize user's Wagtail groups based on email roles.

        Args:
            user: User object
            email_roles: List of email role identifiers
        """
        groups_to_add = []

        for email_role in email_roles:
            group = cls.get_group_for_email_role(email_role)
            if group:
                groups_to_add.append(group)

        # Update user's groups
        user.groups.set(groups_to_add)
