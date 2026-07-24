"""
Authentication and user-related models for django-fusion.

Provides models for user roles, role assignments, and authentication tokens.
"""

from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.Model):
    """
    Role assignment for users with hierarchical permissions.
    Supports multiple roles per user.
    """

    class Role(models.TextChoices):
        SUPERVISOR = 'supervisor', 'Supervisor'
        MANAGER = 'manager', 'Manager'
        INSTRUCTOR = 'instructor', 'Instructor'
        CONTENT_MANAGER = 'content_manager', 'Content Manager'

    # Role hierarchy (higher number = higher privilege)
    ROLE_HIERARCHY = {
        Role.SUPERVISOR: 4,
        Role.MANAGER: 3,
        Role.INSTRUCTOR: 2,
        Role.CONTENT_MANAGER: 1,
    }

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='df_roles'
    )
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        db_index=True
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='df_assigned_roles'
    )

    class Meta:
        app_label = 'django_fusion'
        db_table = 'df_user_role'
        unique_together = [['user', 'role']]
        ordering = ['user', '-role']

    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"

    @classmethod
    def get_highest_role(cls, user):
        """Get the highest role for a user based on hierarchy."""
        user_roles = cls.objects.filter(user=user).values_list('role', flat=True)
        if not user_roles:
            return None

        highest = max(user_roles, key=lambda r: cls.ROLE_HIERARCHY.get(r, 0))
        return highest

    @classmethod
    def has_permission(cls, user, required_role):
        """Check if user has required role or higher."""
        user_highest = cls.get_highest_role(user)
        if not user_highest:
            return False

        user_level = cls.ROLE_HIERARCHY.get(user_highest, 0)
        required_level = cls.ROLE_HIERARCHY.get(required_role, 0)
        return user_level >= required_level


class Role(models.Model):
    """
    Role model for defining user roles and permissions within the system.
    """

    class RoleType(models.TextChoices):
        ADMIN = "ADMIN", _("Administrator")
        MANAGER = "MANAGER", _("Manager")
        EDITOR = "EDITOR", _("Editor")
        CONTRIBUTOR = "CONTRIBUTOR", _("Contributor")
        VIEWER = "VIEWER", _("Viewer")
        CUSTOM = "CUSTOM", _("Custom")

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Role Name"),
        help_text=_("Unique name for this role (e.g., Admin, Manager, User)."),
    )

    role_type = models.CharField(
        max_length=20,
        choices=RoleType.choices,
        default=RoleType.CUSTOM,
        verbose_name=_("Role Type"),
        help_text=_("Category of role"),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Detailed description of this role"),
    )

    permissions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Permissions"),
        help_text=_("JSON structure defining role permissions"),
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Is Default Role"),
        help_text=_("Assign this role to new users by default"),
    )

    level = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Role Level"),
        help_text=_("Hierarchical level (higher = more permissions)"),
    )

    group = models.OneToOneField(
        Group,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Group"),
        help_text=_("Link to a Django group"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'django_fusion'
        db_table = 'role'
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ["level", "name"]
        indexes = [
            models.Index(fields=["role_type"]),
            models.Index(fields=["is_default"]),
            models.Index(fields=["level"]),
        ]

    def __str__(self):
        return self.name

    def has_permission(self, perm_codename):
        """Check if this role has a specific permission."""
        if self.group:
            return self.group.permissions.filter(codename=perm_codename).exists()
        return False


__all__ = ['UserRole', 'Role']
