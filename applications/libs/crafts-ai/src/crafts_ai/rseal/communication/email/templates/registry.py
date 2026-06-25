"""
EmailTemplateRegistry
=====================
Class-level registry for named email templates.

Usage::

    from crafts_ai.communication.email import EmailTemplateRegistry

    EmailTemplateRegistry.register("welcome", "emails/welcome.html", role="user")
    info = EmailTemplateRegistry.get("welcome")
    # {"path": "emails/welcome.html", "role": "user"}

    by_role = EmailTemplateRegistry.get_by_role("user")
    all_templates = EmailTemplateRegistry.list_templates()
"""

from __future__ import annotations

from typing import Dict, Optional


class EmailTemplateRegistry:
    """Class-level registry for named email templates."""

    _registry: Dict[str, Dict] = {}

    @classmethod
    def register(cls, name: str, template_path: str, role: str | None = None) -> None:
        """Register a template under *name*.

        Args:
            name: Unique template identifier.
            template_path: Path to the Django template file.
            role: Optional role this template is associated with.
        """
        cls._registry[name] = {
            "path": template_path,
            "role": role,
        }

    @classmethod
    def get(cls, name: str) -> Optional[Dict]:
        """Return the registration dict for *name*, or ``None``."""
        return cls._registry.get(name)

    @classmethod
    def list_templates(cls) -> Dict:
        """Return a shallow copy of the full registry."""
        return dict(cls._registry)

    @classmethod
    def get_by_role(cls, role: str) -> Optional[Dict]:
        """Return the first registration whose ``role`` matches *role*, or ``None``."""
        for _name, info in cls._registry.items():
            if info.get("role") == role:
                return info
        return None
