"""
Template Resolution for Routes.

Provides intelligent template path resolution for routable components,
cascading through site-specific, shared asset, and fallback templates.

Template Cascade Strategy
--------------------------
For any component, templates are resolved in this order:

1. **Site-specific**: applications/<site>/templates/
2. **Shared assets**: applications/assets/templates/
3. **Django-fusion fallback**: django_fusion/comp/routes/templates/

This allows sites to override shared templates while maintaining
consistency across the platform.

Usage
-----
Inherit from TemplateResolverMixin in RoutableComponent::

    from django_fusion.routes import RoutableComponent, TemplateResolverMixin

    class ProfileComponent(RoutableComponent, TemplateResolverMixin):
        route_name = "profile"
        route_path = "profile/"
        template_name = "profile/detail.html"

        def get_template_paths(self) -> list[str]:
            # Adds site-specific and asset fallbacks automatically
            return super().get_template_paths()
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class TemplateResolverMixin:
    """
    Mixin for intelligent template path resolution.

    Cascades template lookup through:
    1. Site-specific templates (applications/<site>/templates/)
    2. Shared asset templates (applications/assets/templates/)
    3. Django-fusion templates (django_fusion/...)

    This allows each site to override shared templates while
    maintaining fallback to shared/package defaults.
    """

    # Template name to resolve
    template_name: str | None = None

    def get_site_name(self) -> str | None:
        """
        Get the current site name from the resolver match or request.

        Returns:
            Site name (e.g., "lms", "ctc-research") or None
        """
        # Try to get from resolver_match if available
        if hasattr(self, "request") and self.request:
            match = getattr(self.request, "resolver_match", None)
            if match and hasattr(match, "namespace"):
                # Namespace often corresponds to site name
                return match.namespace

        # Try to get from viewset context
        if hasattr(self, "_parent") and self._parent:
            if hasattr(self._parent, "site_name"):
                return self._parent.site_name

        return None

    def get_asset_template_path(self, template_name: str) -> str:
        """
        Convert template name to asset template path.

        Args:
            template_name: Original template name

        Returns:
            Path in shared assets
        """
        return template_name

    def get_site_template_path(self, template_name: str, site_name: str) -> str:
        """
        Convert template name to site-specific template path.

        Args:
            template_name: Original template name
            site_name: Site identifier

        Returns:
            Path in site-specific templates
        """
        # Keep the same path structure, will be resolved in site's template dirs
        return template_name

    def get_django_fusion_template_path(self, template_name: str) -> str:
        """
        Convert template name to django-fusion fallback path.

        Prefixes with django_fusion namespace.

        Args:
            template_name: Original template name

        Returns:
            Path in django-fusion package
        """
        return f"django_fusion/{template_name}"

    def get_template_names(self) -> list[str]:
        """
        Get list of template names to try in resolution order.

        Cascades through:
        1. Site-specific template path
        2. Shared asset template path
        3. Django-fusion fallback path

        Returns:
            List of template names in priority order
        """
        if not self.template_name:
            return []

        templates = []
        site_name = self.get_site_name()

        # Site-specific template (highest priority)
        if site_name:
            site_template = self.get_site_template_path(self.template_name, site_name)
            templates.append(site_template)

        # Shared asset template (medium priority)
        asset_template = self.get_asset_template_path(self.template_name)
        templates.append(asset_template)

        # Django-fusion fallback (lowest priority)
        fusion_template = self.get_django_fusion_template_path(self.template_name)
        templates.append(fusion_template)

        return templates

    def get_template_names_with_fallback(
        self, primary_names: list[str] | None = None
    ) -> list[str]:
        """
        Combine primary template names with cascade fallbacks.

        Args:
            primary_names: Primary template names to try first

        Returns:
            Complete list with cascades applied
        """
        templates = primary_names or []

        # Apply cascade to each primary template
        cascaded = []
        for template_name in templates:
            self.template_name = template_name
            cascaded.extend(self.get_template_names())

        return cascaded or templates


# Example usage patterns documented in docstrings
__all__ = [
    "TemplateResolverMixin",
]
