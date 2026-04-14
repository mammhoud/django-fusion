"""
Email template selection and rendering utilities.

This module provides utilities for selecting and rendering role-based email templates.
"""

from typing import Dict, Optional, Tuple

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class EmailTemplateSelector:
    """Selects and renders email templates based on user role."""

    # Role to template mapping
    ROLE_TEMPLATES = {
        'admin': 'email_templates/admin/base.html',
        'supervisor': 'email_templates/supervisor/base.html',
        'user': 'email_templates/user/base.html',
        'default': 'email_templates/base.html',
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
        context: Dict,
        use_legacy: bool = False
    ) -> Tuple[str, str]:
        """
        Render email template for a given role.

        Args:
            role: User role
            context: Template context dictionary
            use_legacy: Use legacy templates if True

        Returns:
            Tuple of (html_content, text_content)
        """
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
    def get_role_context(cls, role: str) -> Dict:
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
    ) -> Dict:
        """
        Build complete template context.

        Args:
            email: User email address
            role: User role
            **kwargs: Additional context variables

        Returns:
            Complete context dictionary
        """
        context = {
            'email': email,
            'role': role,
            'site_name': getattr(settings, 'SITE_NAME', 'Structa'),
            'site_url': getattr(settings, 'SITE_URL', 'https://structa.cloud'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@structa.cloud'),
        }

        # Add role-specific context
        role_context = cls.get_role_context(role)
        context.update(role_context)

        # Add any additional context
        context.update(kwargs)

        return context


class EmailTemplateRegistry:
    """Registry for managing email templates."""

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
    def get(cls, name: str) -> Optional[Dict]:
        """
        Get registered template.

        Args:
            name: Template name

        Returns:
            Template information or None
        """
        return cls._templates.get(name)

    @classmethod
    def list_templates(cls) -> Dict:
        """
        List all registered templates.

        Returns:
            Dictionary of registered templates
        """
        return cls._templates.copy()

    @classmethod
    def get_by_role(cls, role: str) -> Optional[Dict]:
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
EmailTemplateRegistry.register('admin', 'email_templates/admin/base.html', 'admin')
EmailTemplateRegistry.register('supervisor', 'email_templates/supervisor/base.html', 'supervisor')
EmailTemplateRegistry.register('user', 'email_templates/user/base.html', 'user')
EmailTemplateRegistry.register('base', 'email_templates/base.html', 'default')
