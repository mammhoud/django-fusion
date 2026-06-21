"""
RoleBasedEmailTemplateSelector
================================
Selects and renders role-based email templates.

Usage::

    selector = RoleBasedEmailTemplateSelector(
        site_name="Structa",
        site_url="https://structa.cloud",
        support_email="support@example.com",
    )
    path = selector.get_template_path("admin")
    html, text = selector.render_email("admin", context)
    ctx = selector.build_context("user@example.com", "admin")
"""

from __future__ import annotations

from typing import Dict, Tuple

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class RoleBasedEmailTemplateSelector:
    """Selects and renders role-based email templates.

    Constructor arguments override Django settings; if omitted the selector
    falls back to ``settings.WAGTAIL_SITE_NAME``, ``settings.WAGTAILADMIN_BASE_URL``,
    and ``settings.DEFAULT_FROM_EMAIL``.

    Subclass and override ``ROLE_TEMPLATES`` / ``LEGACY_TEMPLATES`` to
    customise the template paths for a specific website.
    """

    ROLE_TEMPLATES: Dict[str, str] = {
        "admin": "components/email/admin/base.html",
        "supervisor": "components/email/supervisor/base.html",
        "user": "components/email/user/base.html",
        "default": "components/email/base.html",
    }

    LEGACY_TEMPLATES: Dict[str, str] = {
        "admin": "components/email/legacy/admin/base.html",
        "default": "components/email/legacy/base.html",
    }

    def __init__(
        self,
        site_name: str | None = None,
        site_url: str | None = None,
        support_email: str | None = None,
    ) -> None:
        self._site_name = site_name
        self._site_url = site_url
        self._support_email = support_email

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------

    @property
    def site_name(self) -> str:
        return self._site_name or getattr(settings, "WAGTAIL_SITE_NAME", "")

    @property
    def site_url(self) -> str:
        return self._site_url or getattr(settings, "WAGTAILADMIN_BASE_URL", "")

    @property
    def support_email(self) -> str:
        return self._support_email or getattr(settings, "DEFAULT_FROM_EMAIL", "")

    # ------------------------------------------------------------------
    # Template resolution
    # ------------------------------------------------------------------

    def get_template_path(self, role: str, use_legacy: bool = False) -> str:
        """Return the template path for *role*.

        Falls back to the ``"default"`` entry for unknown roles.  Never
        returns ``None`` or an empty string.
        """
        templates = self.LEGACY_TEMPLATES if use_legacy else self.ROLE_TEMPLATES
        return templates.get(role) or templates.get("default") or "components/email/base.html"

    def render_email(
        self,
        role: str,
        context: Dict,
        use_legacy: bool = False,
    ) -> Tuple[str, str]:
        """Render the email template for *role* and return ``(html, text)``.

        Falls back to the default template if the role-specific template
        cannot be rendered.
        """
        template_path = self.get_template_path(role, use_legacy)
        try:
            html_content = render_to_string(template_path, context)
            text_content = strip_tags(html_content)
            return html_content, text_content
        except Exception:
            if role != "default":
                return self.render_email("default", context, use_legacy)
            raise

    # ------------------------------------------------------------------
    # Context helpers
    # ------------------------------------------------------------------

    def get_role_context(self, role: str) -> Dict:
        """Return the default display context for *role*."""
        role_contexts: Dict[str, Dict] = {
            "admin": {
                "role_display": "Administrator",
                "role_color": "#4CAF50",
                "permissions": [
                    "Full system access",
                    "User management",
                    "System configuration",
                    "Audit logs",
                    "Security management",
                    "System monitoring",
                ],
            },
            "supervisor": {
                "role_display": "Supervisor",
                "role_color": "#2196F3",
                "permissions": [
                    "Team management",
                    "Performance monitoring",
                    "Approval workflow",
                    "Reporting",
                    "Quality control",
                    "Training oversight",
                ],
            },
            "user": {
                "role_display": "User",
                "role_color": "#ff9800",
                "permissions": [
                    "Access to resources",
                    "Collaboration tools",
                    "Project management",
                    "Document sharing",
                    "Real-time notifications",
                ],
            },
        }
        return role_contexts.get(
            role,
            {
                "role_display": role.capitalize() if role is not None else "User",
                "role_color": "#666",
                "permissions": [],
            },
        )

    def build_context(self, email: str, role: str, **kwargs) -> Dict:
        """Build the complete template context.

        Always returns a dict containing at minimum:
        ``email``, ``role``, ``site_name``, ``site_url``, ``support_email``.
        """
        context: Dict = {
            "email": email,
            "role": role,
            "site_name": self.site_name,
            "site_url": self.site_url,
            "support_email": self.support_email,
        }
        context.update(self.get_role_context(role))
        context.update(kwargs)
        return context
