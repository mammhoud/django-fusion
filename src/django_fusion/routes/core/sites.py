# All Rights Reserved.

"""
Site and Application routing for django-fusion.

This module provides the Site and Application classes for declarative,
class-based URL routing in Django. It allows organizing viewsets into
hierarchical structures with menu integration.

Classes:
    AppMenuMixin: A route that can be listed in an Application menu.
    Application: A viewset that represents an application with menu items.
    Site: A top-level viewset that contains applications.

The routing follows the pattern: Site → Application → Viewset
Each level can define its own URL patterns, permissions, and menu items.

Example:
    class MySite(Site):
        class MyApp(Application):
            pass
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

from django.urls import NoReverseMatch, include, path
from django.utils.functional import cached_property

from django_fusion.contrib import camel_case_to_title, strip_suffixes
from django_fusion.routes.http.notifications import NotificationMixin

from .base import IndexViewMixin, Viewset

T = TypeVar("T")


class AppMenuMixin:
    """A route that can be listed in an Application menu."""

    title: str | None = None
    icon: str = "view_carousel"

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)

        if name == "title" and attr is None:
            class_title = camel_case_to_title(
                strip_suffixes(self.__class__.__name__, ["Viewset", "Admin", "App", "Flow"])
            )
            if not class_title:
                raise ValueError("Application item needs a title")
            return class_title + "s"

        return attr

    def has_view_permission(self, user: Any, obj: Any | None = None) -> bool:
        parent_class = super()
        if hasattr(parent_class, "has_view_permission"):
            # Use type ignore because the parent might not be correctly typed
            return parent_class.has_view_permission(user, obj=obj)  # type: ignore
        return True


class Application(NotificationMixin, IndexViewMixin, Viewset):
    """
    Application — routing container with notification support.

    Merges ``NotificationMixin`` (from PageHandler) with ``IndexViewMixin``
    and ``Viewset`` so every Application can send notifications and share
    context with its child views.

    Context propagation
    -------------------
    ``application_context()`` returns a dict that child ``RoutableComponent``
    subclasses should merge into their own context.  Override this method
    to inject shared navigation, site info, or other app-level data.
    """

    title: str = ""
    icon: str = "view_module"
    menu_template_name: str = "side-nav/app_menu.html"
    base_template_name: str = "layouts/base.html"
    permission: str | Callable[[Any], bool] | None = None

    def __init__(self, **initkwargs: Any) -> None:
        # Store the viewsets BEFORE super().__init__() so Viewset.__init__
        # can iterate them.  This enables direct instantiation:
        #
        #   Application(title="My App", viewsets=[...], app_name="my")
        #
        # without requiring a subclass.
        if "viewsets" in initkwargs:
            self.viewsets = initkwargs.pop("viewsets")
        super().__init__(**initkwargs)

        # Auto-generate app_name from title when not explicitly set
        if not self.app_name and self.title:
            self.app_name = self.title.lower().replace(" ", "_").replace("-", "_")

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)

        if name == "title" and attr is not None and not attr:
            title = camel_case_to_title(
                strip_suffixes(
                    self.__class__.__name__,
                    ["Application", "Viewset", "Admin", "App", "Flow", "Page"],
                )
            )
            if not title:
                raise ValueError("Application needs a title")

            return title

        return attr

    def _get_resolver_extra(self) -> dict[str, Any]:
        return {"viewset": self, "app": self}

    def get_context_data(self, request: Any, **kwargs) -> dict[str, Any]:
        if not hasattr(self, "name") or not self.name:
            name = self.title.lower().replace(" ", "_")
            self.name = name
        context = {
            "app_name": self.name,
            "title": self.title,
            "icon": self.icon,
            "app_url": request.path,
            "viewset": self,
        }
        # Merge in application_context() — subclasses override this to inject
        # shared data (navigation, site info, etc.) into every child view.
        app_ctx = self.application_context(request)
        if app_ctx:
            context.update(app_ctx)
        return context

    def application_context(self, request: Any) -> dict[str, Any]:
        """
        Shared context injected into every child view.

        Override in subclasses to provide navigation, site branding,
        or other app-level data without repeating it in every view.

        Called by ``get_context_data()`` — the result is merged into
        the context dict returned to child ``RoutableComponent`` views.
        """
        return {}

    def has_view_permission(self, user: Any, obj: Any | None = None) -> bool:
        if self.permission is not None:
            if callable(self.permission):
                return self.permission(user)
            return user.is_authenticated and user.has_perm(self.permission)
        return True

    # ------------------------------------------------------------------
    # URL pattern shortcut for direct include()
    # ------------------------------------------------------------------

    @property
    def url_pattern(self) -> URLPattern:
        """Return a URL pattern ready for ``include()`` in urlpatterns.

        Shortcut that avoids the manual ``(app.urls[0], app.urls[1])``
        tuple unpacking.  Usage::

            urlpatterns += [path("", include(app.url_pattern))]

        Equivalent to::

            urlpatterns += [
                path("", include((app.urls[0], app.urls[1]), namespace=app.urls[2]))
            ]
        """
        return path("", include((self.urls[0], self.urls[1]), namespace=self.urls[2]))

    def menu_items(self) -> Iterator[AppMenuMixin | dict[str, Any]]:
        # First yield the viewsets that are AppMenuMixin instances, sorted by menu_order
        children = [v for v in self._children if isinstance(v, AppMenuMixin)]
        children.sort(key=lambda v: getattr(v, "menu_order", 100))

        for viewset in children:
            if getattr(viewset, "show_in_menu", True):
                yield viewset

        # Then yield URL patterns created with menu_path() as menu items
        for url_pattern in self._get_urls():
            # Check if this is a URLPattern with an icon attribute (created with menu_path)
            if hasattr(url_pattern, "icon"):
                # Create a dictionary with the necessary properties for menu rendering
                menu_item = {
                    "title": getattr(
                        url_pattern,
                        "title",
                        url_pattern.name.replace("_", " ").title() if url_pattern.name else "",
                    ),
                    "icon": getattr(url_pattern, "icon", "dashboard"),
                    "name": url_pattern.name,
                    "pattern": url_pattern.pattern,
                    "is_url_pattern": True,
                }
                yield menu_item


class Site(IndexViewMixin, Viewset):
    title: str | None = None
    icon: str = "view_comfy"
    menu_template_name: str = "side-nav/site_menu.html"
    primary_color: str | None = None
    secondary_color: str | None = None
    permission: str | None = None

    def __init__(self, *, title: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        if title is not None:
            self.title = title

        if self.title is None:
            # pluralize class name
            self.title = camel_case_to_title(strip_suffixes(self.__class__.__name__, ["Site"]))
            if not self.title:
                self.title = "Template Title"

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)

        if name == "title" and attr is None:
            title = camel_case_to_title(strip_suffixes(self.__class__.__name__, ["Site"]))
            if not title:
                title = "Template Title"
            return title

        return attr

    def _get_resolver_extra(self) -> dict[str, Any]:
        return {"viewset": self, "site": self}

    def menu_items(self) -> Iterator[Site | Application]:
        for viewset in self._children:
            if isinstance(viewset, Site | Application):
                yield viewset

    def has_view_permission(self, user: Any, obj: Any | None = None) -> bool:
        if self.permission is not None:
            return user.has_perm(self.permission)
        return True

    def register(self, app_class: type[T]) -> type[T]:
        app = app_class()
        app._parent = self  # type: ignore

        # Initialize viewsets if not already done
        if getattr(self, "viewsets", None) is None:
            self.viewsets = []

        self.viewsets.append(app)  # type: ignore
        return app_class

    @cached_property
    def _viewset_models(self) -> dict[Any, Any]:
        result: dict[Any, Any] = {}

        queue = list(self._children)
        while queue:
            viewset = queue.pop(0)
            if (
                hasattr(viewset, "model")
                and hasattr(viewset, "get_object_url")
                and viewset.model not in result
            ):
                result[viewset.model] = viewset

            # Use getattr to access _children since some types might not have it defined
            children = getattr(viewset, "_children", [])
            for child_viewset in children:
                if isinstance(child_viewset, Viewset):
                    queue.append(child_viewset)
        return result

    def get_absolute_url(self, request: Any, obj: Any) -> str:
        model = type(obj)
        if model in self._viewset_models:
            viewset = self._viewset_models[model]
            # We know get_object_url exists because we checked in _viewset_models
            return viewset.get_object_url(request, obj)  # type: ignore
        else:
            raise NoReverseMatch(f"Viewset for {model.__name__} not found")

    # ------------------------------------------------------------------
    # URL pattern shortcut for direct include()
    # ------------------------------------------------------------------

    @property
    def url_pattern(self) -> URLPattern:
        """Return a URL pattern ready for ``include()`` in urlpatterns.

        Shortcut that avoids the manual ``(site.urls[0], site.urls[1])``
        tuple unpacking.  Usage::

            urlpatterns += [path("", include(site.url_pattern))]

        Equivalent to::

            urlpatterns += [
                path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2]))
            ]
        """
        return path("", include((self.urls[0], self.urls[1]), namespace=self.urls[2]))