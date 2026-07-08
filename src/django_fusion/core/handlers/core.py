"""
Core handler classes and utilities for django_fusion.

This module contains core handler functionality that is pure Django
and can be used across projects without Wagtail dependencies.
"""

from typing import List, Set, Tuple

from django.contrib.auth.models import Group, Permission, User
from django.db import transaction


class RoleHierarchyManager:
    """
    Manages role hierarchy and permission inheritance.

    This class provides utilities for managing Django groups, roles, and permissions
    with support for role hierarchy and permission inheritance.
    """

    # Define role hierarchy: parent roles inherit permissions from child roles
    ROLE_HIERARCHY = {
        "admin": ["supervisor", "user"],
        "supervisor": ["user"],
        "user": [],
    }

    # Define permissions for each role
    ROLE_PERMISSIONS = {
        "admin": [
            "auth.add_user",
            "auth.change_user",
            "auth.delete_user",
            "auth.add_group",
            "auth.change_group",
            "auth.delete_group",
            "auth.add_permission",
            "auth.change_permission",
            "auth.delete_permission",
        ],
        "supervisor": [
            "auth.change_user",
            "auth.view_user",
            "auth.add_group",
            "auth.change_group",
            "auth.view_group",
        ],
        "user": [
            "auth.view_user",
            "auth.view_group",
        ],
    }

    def __init__(self):
        """Initialize the role hierarchy manager."""
        self.permission_cache = {}

    def get_all_permissions_for_role(self, role: str) -> Set[str]:
        """
        Get all permissions for a role, including inherited permissions.

        Args:
            role: The role name

        Returns:
            Set of permission strings
        """
        if role in self.permission_cache:
            return self.permission_cache[role]

        permissions = set(self.ROLE_PERMISSIONS.get(role, []))

        # Add inherited permissions from child roles
        for child_role in self.ROLE_HIERARCHY.get(role, []):
            permissions.update(self.get_all_permissions_for_role(child_role))

        self.permission_cache[role] = permissions
        return permissions

    def get_role_hierarchy(self, role: str) -> List[str]:
        """
        Get all roles in the hierarchy for a given role.

        Args:
            role: The role name

        Returns:
            List of role names in the hierarchy
        """
        hierarchy = [role]
        for child_role in self.ROLE_HIERARCHY.get(role, []):
            hierarchy.extend(self.get_role_hierarchy(child_role))
        return hierarchy

    @transaction.atomic
    def create_or_update_group(self, role: str) -> Tuple[Group, bool]:
        """
        Create or update a group with appropriate permissions.

        Args:
            role: The role name

        Returns:
            Tuple of (group, created)
        """
        group, created = Group.objects.get_or_create(name=role)

        # Get all permissions for this role
        permission_codenames = self.get_all_permissions_for_role(role)

        # Get permission objects
        permissions = []
        for perm_string in permission_codenames:
            try:
                app_label, codename = perm_string.split(".")
                perm = Permission.objects.get(
                    content_type__app_label=app_label, codename=codename
                )
                permissions.append(perm)
            except Permission.DoesNotExist:
                # Permission doesn't exist, skip it
                pass

        # Set permissions for the group
        group.permissions.set(permissions)

        return group, created

    @transaction.atomic
    def assign_user_to_role(self, user: User, role: str) -> bool:
        """
        Assign a user to a role (and all parent roles in hierarchy).

        Args:
            user: The user to assign
            role: The role name

        Returns:
            True if successful
        """
        # Get all roles in the hierarchy
        roles = self.get_role_hierarchy(role)

        # Clear existing groups
        user.groups.clear()

        # Add user to all roles in hierarchy
        for r in roles:
            try:
                group = Group.objects.get(name=r)
                user.groups.add(group)
            except Group.DoesNotExist:
                # Create the group if it doesn't exist
                group, _ = self.create_or_update_group(r)
                user.groups.add(group)

        return True

    @transaction.atomic
    def assign_user_to_multiple_roles(self, user: User, roles: List[str]) -> bool:
        """
        Assign a user to multiple roles.

        Args:
            user: The user to assign
            roles: List of role names

        Returns:
            True if successful
        """
        # Clear existing groups
        user.groups.clear()

        # Add user to all specified roles and their hierarchies
        all_roles = set()
        for role in roles:
            all_roles.update(self.get_role_hierarchy(role))

        for r in all_roles:
            try:
                group = Group.objects.get(name=r)
                user.groups.add(group)
            except Group.DoesNotExist:
                # Create the group if it doesn't exist
                group, _ = self.create_or_update_group(r)
                user.groups.add(group)

        return True

    def get_user_roles(self, user: User) -> List[str]:
        """
        Get all roles for a user.

        Args:
            user: The user

        Returns:
            List of role names
        """
        return list(user.groups.values_list("name", flat=True))

    def get_user_permissions(self, user: User) -> Set[str]:
        """
        Get all permissions for a user through their groups.

        Args:
            user: The user

        Returns:
            Set of permission strings
        """
        permissions = set()

        # Get permissions from user's groups
        for group in user.groups.all():
            for perm in group.permissions.all():
                permissions.add(f"{perm.content_type.app_label}.{perm.codename}")

        # Add direct user permissions
        for perm in user.user_permissions.all():
            permissions.add(f"{perm.content_type.app_label}.{perm.codename}")

        return permissions

    def has_role(self, user: User, role: str) -> bool:
        """
        Check if user has a specific role.

        Args:
            user: The user
            role: The role name

        Returns:
            True if user has the role
        """
        return user.groups.filter(name=role).exists()

    def has_permission(self, user: User, permission: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            user: The user
            permission: The permission string (e.g., "app.codename")

        Returns:
            True if user has the permission
        """
        if user.is_superuser:
            return True

        try:
            app_label, codename = permission.split(".")
            return user.has_perm(f"{app_label}.{codename}")
        except ValueError:
            return False


class GroupAccessControl:
    """
    Manages group-based access control.

    This class provides utilities for checking group membership and filtering
    querysets by user groups.
    """

    @staticmethod
    def check_group_access(user: User, required_groups: List[str]) -> bool:
        """
        Check if user belongs to any of the required groups.

        Args:
            user: The user
            required_groups: List of required group names

        Returns:
            True if user belongs to any required group
        """
        if user.is_superuser:
            return True

        user_groups = set(user.groups.values_list("name", flat=True))
        required_set = set(required_groups)

        return bool(user_groups & required_set)

    @staticmethod
    def check_role_access(user: User, required_role: str) -> bool:
        """
        Check if user has a specific role.

        Args:
            user: The user
            required_role: The required role name

        Returns:
            True if user has the role
        """
        if user.is_superuser:
            return True

        return user.groups.filter(name=required_role).exists()

    @staticmethod
    def get_accessible_groups(user: User) -> List[Group]:
        """
        Get all groups accessible to a user.

        Args:
            user: The user

        Returns:
            List of groups
        """
        if user.is_superuser:
            return list(Group.objects.all())

        return list(user.groups.all())

    @staticmethod
    def filter_by_group(queryset, user: User, group_field: str = "groups"):
        """
        Filter a queryset by user's groups.

        Args:
            queryset: The queryset to filter
            user: The user
            group_field: The field name for groups (default: "groups")

        Returns:
            Filtered queryset
        """
        if user.is_superuser:
            return queryset

        user_groups = user.groups.all()
        return queryset.filter(**{f"{group_field}__in": user_groups}).distinct()



class DynamicComponentRenderer:
    """
    Renderer for dynamic HTML components.

    This handles the loading and rendering of uploaded HTML templates
    using the Django template engine, ensuring they can be used
    within the django-grep component ecosystem.

    Canonical import: from django_fusion.handlers.core import DynamicComponentRenderer
    """

    def render(self, html_file, context) -> str:
        """
        Render an HTML template from a file.

        Args:
            html_file: File object or path to HTML file
            context: Django template context

        Returns:
            Rendered HTML string
        """
        if not html_file:
            return ""

        try:
            import logging

            from django.template import Context, Template
            from django.utils.safestring import mark_safe

            logger = logging.getLogger(__name__)

            if hasattr(html_file, 'open'):
                with html_file.open('r') as f:
                    template_content = f.read()
            else:
                with open(html_file.path, 'r') as f:
                    template_content = f.read()

            # Compile and render
            template = Template(template_content)
            return template.render(context)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[DynamicComponentRenderer] Error: {e}")
            from django.utils.safestring import mark_safe
            return mark_safe(f"<!-- Renderer Error: {e} -->")



class EmailTemplateSelector:
    """
    Selects and renders email templates based on user role.

    Provides role-based email template selection and rendering with
    fallback to default templates.

    Canonical import: from django_fusion.handlers.core import EmailTemplateSelector
    """

    # Role to template mapping
    ROLE_TEMPLATES = {
        'admin': 'components/email/admin/base.html',
        'supervisor': 'components/email/supervisor/base.html',
        'user': 'components/email/user/base.html',
        'default': 'components/email/base.html',
    }

    # Legacy template mapping for backward compatibility
    LEGACY_TEMPLATES = {
        'admin': 'emails/admin_test.html',
        'admin/supervisor': 'emails/admin_supervisor_test.html',
        'supervisor': 'emails/supervisor_test.html',
        'default': 'emails/test_email.html',
    }

    @classmethod
    def get_template_path(cls, role: str, use_legacy: bool = False) -> str:
        """
        Get template path for a given role.

        Args:
            role: User role (admin, supervisor, user, etc.)
            use_legacy: Use legacy template paths if True

        Returns:
            Template path string
        """
        templates = cls.LEGACY_TEMPLATES if use_legacy else cls.ROLE_TEMPLATES
        return templates.get(role, templates.get('default'))

    @classmethod
    def render_email(
        cls,
        role: str,
        context: dict,
        use_legacy: bool = False
    ) -> tuple:
        """
        Render email template for a given role.

        Args:
            role: User role
            context: Template context dictionary
            use_legacy: Use legacy templates if True

        Returns:
            Tuple of (html_content, text_content)
        """
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags

        template_path = cls.get_template_path(role, use_legacy)

        try:
            html_content = render_to_string(template_path, context)
            text_content = strip_tags(html_content)
            return html_content, text_content
        except Exception as e:
            # Fallback to default template
            if role != 'default':
                return cls.render_email('default', context, use_legacy)
            raise

    @classmethod
    def get_role_context(cls, role: str) -> dict:
        """
        Get default context for a role.

        Args:
            role: User role

        Returns:
            Dictionary with role-specific context
        """
        role_contexts = {
            'admin': {
                'role_display': 'Administrator',
                'role_color': '#4CAF50',
                'permissions': [
                    'Full system access',
                    'User management',
                    'System configuration',
                    'Audit logs',
                    'Security management',
                    'System monitoring',
                ]
            },
            'supervisor': {
                'role_display': 'Supervisor',
                'role_color': '#2196F3',
                'permissions': [
                    'Team management',
                    'Performance monitoring',
                    'Approval workflow',
                    'Reporting',
                    'Quality control',
                    'Training oversight',
                ]
            },
            'user': {
                'role_display': 'User',
                'role_color': '#ff9800',
                'permissions': [
                    'Access to resources',
                    'Collaboration tools',
                    'Project management',
                    'Document sharing',
                    'Real-time notifications',
                ]
            },
        }

        return role_contexts.get(role, {
            'role_display': role.capitalize(),
            'role_color': '#666',
            'permissions': []
        })

    @classmethod
    def build_context(
        cls,
        email: str,
        role: str,
        **kwargs
    ) -> dict:
        """
        Build complete template context.

        Args:
            email: User email address
            role: User role
            **kwargs: Additional context variables

        Returns:
            Complete context dictionary
        """
        from django.conf import settings

        context = {
            'email': email,
            'role': role,
            'site_name': getattr(settings, 'SITE_NAME', 'Django Site'),
            'site_url': getattr(settings, 'SITE_URL', 'https://example.com'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com'),
        }

        # Add role-specific context
        role_context = cls.get_role_context(role)
        context.update(role_context)

        # Add any additional context
        context.update(kwargs)

        return context


class EmailTemplateRegistry:
    """
    Registry for managing email templates.

    Provides a centralized registry for email templates with role-based lookup.

    Canonical import: from django_fusion.handlers.core import EmailTemplateRegistry
    """

    _templates = {}

    @classmethod
    def register(cls, name: str, template_path: str, role: str = None):
        """
        Register an email template.

        Args:
            name: Template name
            template_path: Path to template file
            role: Associated role (optional)
        """
        cls._templates[name] = {
            'path': template_path,
            'role': role,
        }

    @classmethod
    def get(cls, name: str):
        """
        Get registered template.

        Args:
            name: Template name

        Returns:
            Template information or None
        """
        return cls._templates.get(name)

    @classmethod
    def list_templates(cls) -> dict:
        """
        List all registered templates.

        Returns:
            Dictionary of registered templates
        """
        return cls._templates.copy()

    @classmethod
    def get_by_role(cls, role: str):
        """
        Get template by role.

        Args:
            role: User role

        Returns:
            Template information or None
        """
        for name, info in cls._templates.items():
            if info.get('role') == role:
                return info
        return None


# Register default templates
EmailTemplateRegistry.register('admin', 'components/email/admin/base.html', 'admin')
EmailTemplateRegistry.register('supervisor', 'components/email/supervisor/base.html', 'supervisor')
EmailTemplateRegistry.register('user', 'components/email/user/base.html', 'user')
EmailTemplateRegistry.register('base', 'components/email/base.html', 'default')
