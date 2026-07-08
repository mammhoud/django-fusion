"""
Forms and Tables Integration for Routes.

This module provides mixins to integrate form handling and table rendering
into routable components, with template resolution that cascades:

1. Site-specific templates (applications/<site>/templates/)
2. Shared asset templates (applications/assets/templates/)
3. Django-fusion fallback templates

Template Path Resolution
------------------------
The resolution follows a hierarchical pattern::

    # Form templates
    applications/<site>/templates/components/form/<name>.html
    applications/assets/templates/components/form/<name>.html
    django_fusion/comp/routes/templates/routable_components/forms/<name>.html

    # Table templates
    applications/<site>/templates/plugins/tables/<name>.html
    applications/assets/templates/plugins/tables/<name>.html
    django_fusion/comp/routes/templates/routable_components/tables/<name>.html

Usage
-----
Combine mixins with RoutableComponent::

    from django_fusion.comp.routes import RoutableComponent
    from django_fusion.comp.routes.forms_tables import FormMixin, TableMixin

    class UserListComponent(RoutableComponent, TableMixin):
        route_name = "users"
        route_path = "users/"
        title = "Users"
        table_name = "users"
        model = User

        def get_table_data(self):
            return User.objects.all()

    class UserCreateComponent(RoutableComponent, FormMixin):
        route_name = "user_create"
        route_path = "users/create/"
        title = "Create User"
        form_name = "user"
        model = User
"""

from __future__ import annotations

from typing import Any

from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.views import generic

from django_fusion.comp.generic.base import FormLayoutMixin


class FormMixin:
    """
    Mixin for rendering forms in routable components.

    Provides template resolution, form handling, and context injection
    for form-based views integrated with routes.

    Attributes:
        form_name (str): Base name for form templates.
            Templates resolved: components/form/{form_name}.html
        form_class (type[Form] | None): Form class for rendering.
        form_kwargs (dict): Additional kwargs passed to form initialization.
    """

    form_name: str | None = None
    form_class: type[Form] | None = None
    form_kwargs: dict[str, Any] | None = None

    def get_form_name(self) -> str:
        """
        Get the form template name.

        Returns:
            Base name for form template lookup (without .html extension)
        """
        if self.form_name:
            return self.form_name
        if hasattr(self, "model") and self.model:
            return self.model._meta.model_name
        raise ValueError(
            f"{self.__class__.__name__} must define form_name or inherit model"
        )

    def get_form_template_names(self) -> list[str]:
        """
        Resolve form template names with fallback chain.

        Template resolution order:
        1. Site-specific: components/form/{form_name}.html
        2. Shared assets: components/form/{form_name}.html
        3. Fallback: django_fusion form template

        Returns:
            List of template names to try in order
        """
        form_name = self.get_form_name()
        return [
            f"components/form/{form_name}.html",
            f"components/form/form.html",  # Generic form fallback
            "django_fusion/comp/routes/templates/routable_components/forms/form.html",
        ]

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Get kwargs for form initialization.

        Returns:
            Dictionary of kwargs for form instantiation
        """
        kwargs = self.form_kwargs or {}
        return kwargs

    def get_form_class(self) -> type[Form]:
        """
        Get the form class for this view.

        Returns:
            Form class
        """
        if self.form_class:
            return self.form_class
        raise ValueError(f"{self.__class__.__name__} must define form_class")

    def get_form(self) -> Form:
        """
        Instantiate and return the form.

        Returns:
            Form instance
        """
        form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_context_data(self) -> dict[str, Any]:
        """
        Get context data specific to form rendering.

        Returns:
            Dictionary with form context
        """
        return {
            "form": self.get_form(),
            "form_name": self.get_form_name(),
        }


class TableMixin:
    """
    Mixin for rendering tables in routable components.

    Provides template resolution, data preparation, and context injection
    for table-based views integrated with routes.

    Attributes:
        table_name (str): Base name for table templates.
            Templates resolved: plugins/tables/{table_name}.html
        table_headers (list[dict]): Column headers configuration.
        table_data (list | None): Table data rows.
    """

    table_name: str | None = None
    table_headers: list[dict[str, Any]] | None = None
    table_data: list[Any] | None = None

    def get_table_name(self) -> str:
        """
        Get the table template name.

        Returns:
            Base name for table template lookup (without .html extension)
        """
        if self.table_name:
            return self.table_name
        if hasattr(self, "model") and self.model:
            return f"{self.model._meta.model_name}_table"
        raise ValueError(
            f"{self.__class__.__name__} must define table_name or inherit model"
        )

    def get_table_template_names(self) -> list[str]:
        """
        Resolve table template names with fallback chain.

        Template resolution order:
        1. Site-specific: plugins/tables/{table_name}.html
        2. Shared assets: plugins/tables/{table_name}.html
        3. Fallback: generic table template

        Returns:
            List of template names to try in order
        """
        table_name = self.get_table_name()
        return [
            f"plugins/tables/{table_name}.html",
            f"plugins/tables/table.html",  # Generic table fallback
            "django_fusion/comp/routes/templates/routable_components/tables/table.html",
        ]

    def get_table_headers(self) -> list[dict[str, Any]]:
        """
        Get table column headers.

        Override this method to define custom headers dynamically.

        Returns:
            List of header dictionaries with keys:
                - label (str): Display name
                - key (str): Data key
                - sortable (bool): Whether column is sortable
                - width (str): Column width (optional)
        """
        if self.table_headers:
            return self.table_headers

        # Auto-generate from model fields if available
        if hasattr(self, "model") and self.model:
            headers = []
            for field in self.model._meta.get_fields():
                if not field.many_to_one and not field.one_to_many:
                    headers.append(
                        {
                            "label": field.verbose_name.title(),
                            "key": field.name,
                            "sortable": True,
                        }
                    )
            return headers

        return []

    def get_table_data(self) -> list[Any]:
        """
        Get table data rows.

        Override this method to fetch or process data.

        Returns:
            List of row objects/dictionaries
        """
        if self.table_data:
            return self.table_data

        # Auto-fetch from queryset if available
        if hasattr(self, "get_queryset"):
            return list(self.get_queryset())

        return []

    def get_table_context_data(self) -> dict[str, Any]:
        """
        Get context data specific to table rendering.

        Returns:
            Dictionary with table context
        """
        return {
            "table_name": self.get_table_name(),
            "table_headers": self.get_table_headers(),
            "table_data": self.get_table_data(),
        }


class FormTableMixin(FormMixin, TableMixin):
    """
    Combined mixin for components using both forms and tables.

    Provides integrated form and table rendering in a single component.
    Useful for search/filter forms above table lists, or inline editing.
    """

    def get_form_table_context_data(self) -> dict[str, Any]:
        """
        Get combined context for form and table rendering.

        Returns:
            Dictionary with both form and table context
        """
        context = {}
        context.update(self.get_form_context_data())
        context.update(self.get_table_context_data())
        return context


# Export for convenience
__all__ = [
    "FormMixin",
    "TableMixin",
    "FormTableMixin",
]
