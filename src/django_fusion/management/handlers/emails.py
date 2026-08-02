"""
Handler classes and utilities for django_fusion — email templates, renderers, roles & access control.

This module provides email template selection/registry, dynamic component rendering,
and role-based access control utilities that are pure Django and can be used across
projects without Wagtail dependencies.

Canonical imports:
    from django_fusion.management.handlers.emails import EmailTemplateRegistry, EmailTemplateSelector
    from django_fusion.management.handlers.emails import DynamicComponentRenderer
    from django_fusion.management.managers.role_hierarchy import RoleHierarchyManager
    from django_fusion.management.managers.group_access import GroupAccessControl
"""

from typing import List, Set, Tuple

from django.contrib.auth.models import Group, Permission, User
from django.db import transaction


class DynamicComponentRenderer:
    """
    Renderer for dynamic HTML components.

    This handles the loading and rendering of uploaded HTML templates
    using the Django template engine, ensuring they can be used
    within the django-grep component ecosystem.

    Canonical import: from django_fusion.management.handlers.emails import DynamicComponentRenderer
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

    Canonical import: from django_fusion.management.handlers.emails import EmailTemplateSelector
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

    Canonical import: from django_fusion.management.handlers.emails import EmailTemplateRegistry
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
