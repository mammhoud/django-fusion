"""
django_fusion.fragments.forms.mixins — Enhanced FormMixin + FormTableMixin.

Provides:
  - FormMixin: Form handling with auto-ModelForm creation and tag generation
  - FormTableMixin: Combined form + table mixin for search/filter views
"""

from __future__ import annotations

from typing import Any

from django.forms import Form, ModelForm

from django_fusion.fragments.forms.tag_generator import FormTagGenerator


class FormMixin:
    """Enhanced mixin for rendering forms in routable components.

    Extends the original ``FormMixin`` with:
      - Auto-ModelForm creation from ``model`` attribute
      - ``FormTagGenerator`` integration for field-level rendering
      - Layout support via ``form_layout``

    Attributes:
        form_name (str | None): Template name for form lookup.
        form_class (type[Form] | None): Explicit Django Form class.
        model (type | None): Django Model for auto-ModelForm creation.
        form_layout (list | None): Field layout groups for display.
        form_field_kwargs (dict | None): Per-field overrides (label, placeholder, etc.).
        tag_generator_class (type): FormTagGenerator class.
    """

    form_name: str | None = None
    form_class: type[Form] | None = None
    form_kwargs: dict[str, Any] | None = None
    form_layout: list | None = None
    form_field_kwargs: dict[str, dict] | None = None
    tag_generator_class: type = FormTagGenerator

    def get_form_name(self) -> str:
        """Get the form template name.

        Returns:
            Base name for form template lookup.
        """
        if self.form_name:
            return self.form_name
        if hasattr(self, "model") and self.model:
            return self.model._meta.model_name
        raise ValueError(
            f"{self.__class__.__name__} must define form_name or inherit model"
        )

    def get_form_template_names(self) -> list[str]:
        """Resolve form template names with fallback chain.

        Returns:
            List of template names tried in order.
        """
        form_name = self.get_form_name()
        return [
            f"components/form/{form_name}.html",
            "components/form/form.html",
        ]

    def get_form_kwargs(self) -> dict[str, Any]:
        """Get kwargs for form initialization."""
        kwargs = self.form_kwargs or {}
        return kwargs

    def get_form_class(self) -> type[Form]:
        """Get the form class.

        Returns the explicit ``form_class`` if set, otherwise creates
        a ``ModelForm`` from the ``model`` attribute.

        Returns:
            Django Form class.
        """
        if self.form_class:
            return self.form_class

        if hasattr(self, "model") and self.model:
            # Auto-create a ModelForm from the model
            model_class = self.model
            form_fields = self._build_modelform_fields(model_class)
            return type(
                f"{model_class.__name__}Form",
                (ModelForm,),
                {
                    "Meta": type("Meta", (), {"model": model_class, "fields": form_fields}),
                },
            )

        raise ValueError(f"{self.__class__.__name__} must define form_class or model")

    def _build_modelform_fields(self, model_class) -> list[str]:
        """Build field list for auto-generated ModelForm.

        Excludes: auto_created fields, relational fields (m2o/o2m),
        auto-timestamp fields (auto_now/auto_now_add), and primary keys.
        """
        fields = []
        for field in model_class._meta.get_fields():
            # Skip relational fields
            if field.auto_created or field.many_to_one or field.one_to_many:
                continue
            # Skip auto-timestamps
            if getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False):
                continue
            # Skip primary keys (auto-generated IDs)
            if field.primary_key and field.auto_created:
                continue
            fields.append(field.name)
        return fields or ["__all__"]

    def get_form(self) -> Form:
        """Instantiate and return the form."""
        form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_tag_generator(self) -> FormTagGenerator:
        """Create a FormTagGenerator for the current form.

        Returns:
            FormTagGenerator configured with layout and field overrides.
        """
        return self.tag_generator_class(
            form=self.get_form(),
            layout=self.form_layout,
            field_kwargs=self.form_field_kwargs,
        )

    def get_form_context_data(self) -> dict[str, Any]:
        """Get context data for form rendering.

        Returns:
            Dictionary with form, form_name, fields, and layout_groups.
        """
        gen = self.get_form_tag_generator()
        return {
            "form": self.get_form(),
            "form_name": self.get_form_name(),
            "fields": gen.get_fields(),
            "layout_groups": gen.get_layout_groups(),
        }


# Direct import — no circular dependency exists because:
# tables/mixins.py → row_generator.py  (no cross-import)
# forms/mixins.py  → tag_generator.py   (no cross-import)
# forms/mixins.py  → tables/mixins.py   (safe, tables doesn't import forms)
from django_fusion.fragments.tables.mixins import TableMixin


class FormTableMixin(FormMixin, TableMixin):
    """Combined mixin for components using both forms and tables.

    Inherits directly from both ``FormMixin`` and ``TableMixin``
    so standalone use provides full form + table capabilities
    without requiring consumers to mix ``TableMixin`` separately.

    Usage::

        class ProductSearch(RoutableComponent, FormTableMixin):
            form_name = "search"
            table_name = "products"
            ...

        # FormTableMixin alone gives both form AND table capabilities.
    """

    form_table_combined: bool = True

    def get_form_table_context_data(self) -> dict[str, Any]:
        """Get combined context for form and table rendering.

        Returns:
            Dictionary with both form and table context dictionaries.
        """
        context = {}
        context.update(self.get_form_context_data())

        if hasattr(self, "get_table_context_data"):
            context.update(self.get_table_context_data())

        return context
