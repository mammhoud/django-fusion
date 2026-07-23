# All Rights Reserved.

"""
Routable Components for django-fusion.

This module provides RoutableComponent, which combines ComponentViews
(rendering pipeline) with BaseViewset (URL routing). It is the correct
base for any view that lives in the root `/` routing tree.

Classes:
    RoutableComponent: Full-page routable view registered in the Site → Application tree.

RoutableComponent extends ComponentViews with:
- route_path / route_name: URL pattern and name
- urls property: Generates a single-route _URLResolver
- setup(): Calls has_permission() → PermissionDenied
- has_permission(): Checks permission_required
- get_breadcrumbs(): Traverses the parent viewset hierarchy
- Menu integration: menu_label, menu_order, show_in_menu

Template convention:
Set fragment_name (dotted string) to identify the fragment template:
    fragment_name = "profile.dashboard"
    # → resolves to "profile/dashboard.html" when strategy == "fragment"

If ``fragment_name`` is not explicitly set, ``get_fragment_name()`` derives
a default from ``route_name``::

    route_name = "dashboard"
    # → get_fragment_name() returns "components.dashboard"
    # → resolves to "components/dashboard.html"

This default links the component to the package's ``components/`` template
directory (``django_fusion/comp/templates/components/``), so every
``RoutableComponent`` has a sensible fragment path without manual
configuration.

For the full-page template set template_name as usual.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.urls import URLResolver, path
from django.urls.resolvers import RoutePattern

from django_fusion.site.interface._context_mixins import is_htmx_request
from django_fusion.site.interface.page_handler import ComponentViews

from .base import BaseViewset, _URLResolver


class RoutableComponent(ComponentViews, BaseViewset):
    """
    Full-page routable view registered in the ``Site → Application`` tree.

    Extends ``ComponentViews`` with:

    * ``route_path`` / ``route_name`` — URL pattern and name.
    * ``urls`` property — generates a single-route ``_URLResolver``.
    * ``setup()`` — calls ``has_permission()`` → ``PermissionDenied``.
    * ``has_permission()`` — checks ``permission_required``.
    * ``get_breadcrumbs()`` — traverses the parent viewset hierarchy.
    * Menu integration: ``menu_label``, ``menu_order``, ``show_in_menu``. or 

    Template convention
    -------------------
    Set ``fragment_name`` (dotted string) to identify the fragment template::

        fragment_name = "profile.dashboard"
        # → resolves to "profile/dashboard.html" when strategy == "fragment"

    If ``fragment_name`` is not set, ``get_fragment_name()`` derives a default
    from ``route_name``::

        route_name = "dashboard"
        # → get_fragment_name() returns "components.dashboard"
        # → resolves to "components/dashboard.html"

    For the full-page template set ``template_name`` as usual.

    Example::

        class DashboardComponent(RoutableComponent):
            route_name = "dashboard"
            route_path = "dashboard/"
            title = "Dashboard"
            fragment_name = "lms.dashboard"
            template_name = "lms/dashboard.html"

            def has_permission(self, user):
                return user.is_staff
    """

    route_name: str | None = None
    route_path: str = ""
    icon: str = "view_carousel"
    title: str | None = None
    permission_required: str | list[str] | None = None

    # Menu integration
    menu_label: str | None = None
    menu_order: int = 100
    show_in_menu: bool = True

    # page_title alias — kept for backward compat with PageHandler-style views
    page_title: str | None = None  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Fragment name — default derived from route_name
    # ------------------------------------------------------------------

    def get_fragment_name(self) -> str | None:
        """Return the dotted fragment identifier, with a default derivation.

        If ``fragment_name`` is explicitly set, it is returned as-is.

        Otherwise the default is derived from ``route_name`` so every
        routable component has a fragment path without manual configuration::

            route_name = "dashboard"
            # → "components.dashboard"
            # → template: "components/dashboard.html"

        This links the component to the package's ``components/`` template
directory
        (``django_fusion/comp/templates/components/``), which is registered
        via ``APP_DIRS`` and ``COMPONENT_DIRS`` in the project template
        configuration.

        Returns ``None`` when neither ``fragment_name`` nor ``route_name``
        is set.
        """
        if self.fragment_name:
            return self.fragment_name
        if self.route_name:
            return f"components.{self.route_name}"
        return None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Guarantee _parent is present — View.__init__ breaks the MRO chain.
        self._init_viewset()

    # ------------------------------------------------------------------
    # URL generation
    # ------------------------------------------------------------------

    @property
    def urls(self) -> tuple[list[URLResolver], str | None, str | None]:
        """Generate a single-route resolver from ``route_path``."""
        if not self.route_path:
            raise ValueError(
                f"{self.__class__.__name__} must define route_path"
            )
        name = self.route_name or self.__class__.__name__.lower()
        url_pattern = path(self.route_path, type(self).as_view(), name=name)
        resolver = _URLResolver(
            RoutePattern("", is_endpoint=False),
            [url_pattern],
            extra={"viewset": self},
        )
        return [resolver], self.app_name, self.namespace or self.app_name

    # ------------------------------------------------------------------
    # Permission checking
    # ------------------------------------------------------------------

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().setup(request, *args, **kwargs)
        if not self.has_permission(request.user):
            raise PermissionDenied("You don't have permission to access this resource")

    def has_permission(self, user: Any) -> bool:
        """Check ``permission_required`` (string or list).  Override freely."""
        if self.permission_required is None:
            return True
        if isinstance(self.permission_required, str):
            return user.has_perm(self.permission_required)
        return all(user.has_perm(p) for p in self.permission_required)

    # ------------------------------------------------------------------
    # URL reversing
    # ------------------------------------------------------------------

    def get_route_url(self, *args: Any, **kwargs: Any) -> str:
        """Return the namespaced URL for this component."""
        if self.route_name is None:
            raise ValueError(f"{self.__class__.__name__} must define route_name")
        return self.reverse(self.route_name, args=args, kwargs=kwargs)

    # ------------------------------------------------------------------
    # Breadcrumbs — hierarchy-aware
    # ------------------------------------------------------------------

    def get_breadcrumbs(self) -> list[dict[str, str]]:
        """Build breadcrumbs by traversing the parent viewset hierarchy."""
        from django.urls.exceptions import NoReverseMatch

        breadcrumbs: list[dict[str, str]] = []
        for parent in self.parents():
            if hasattr(parent, "title") and hasattr(parent, "get_route_url"):
                try:
                    breadcrumbs.append(
                        {
                            "title": parent.title or parent.__class__.__name__,
                            "url": parent.get_route_url(),
                        }
                    )
                except (ValueError, AttributeError, NoReverseMatch):
                    continue
        if self.title:
            try:
                breadcrumbs.append({"title": self.title, "url": self.get_route_url()})
            except (ValueError, NoReverseMatch):
                breadcrumbs.append({"title": self.title, "url": "#"})
        return breadcrumbs

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        effective_title = self.title or self.page_title or self.menu_label
        context.update(
            {
                "breadcrumbs": self.get_breadcrumbs(),
                "title": effective_title,
                "page_title": effective_title,
                "icon": self.icon,
                "component": self,
            }
        )
        return context
