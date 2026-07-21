"""
django_fusion.comp.contrib.forms.tag_generator — Form field → HTML context.

Parses Django Form/ModelForm instances and generates field-level context
dictionaries that template tags consume for rendering.

Usage::

    generator = FormTagGenerator(form_instance, layout=[["name", "email"]])
    fields = generator.get_fields()  # → [{"name": "name", "widget": "text", ...}]
"""

from __future__ import annotations

from typing import Any

from django.forms import Form


class FormTagGenerator:
    """Generate renderable form field context from Django form instances.

    Parses each field's widget type, label, help text, CSS classes, and
    validation state into a dictionary that templates can iterate over.

    Usage::

        gen = FormTagGenerator(my_form, layout=[["name", "price"], ["description"]])
        context = {"fields": gen.get_fields()}
        # Render in template: {% for field in fields %} ... {% endfor %}
    """

    def __init__(
        self,
        form: Form,
        layout: list | None = None,
        field_kwargs: dict[str, dict] | None = None,
    ) -> None:
        self._form = form
        self._layout = layout
        self._field_kwargs = field_kwargs or {}

    def get_fields(self) -> list[dict[str, Any]]:
        """Generate field context for all visible form fields.

        Returns:
            List of field dicts with keys: name, label, widget, type,
            value, help_text, required, errors, css_classes, placeholder.

        Fields are ordered by ``layout`` if provided, otherwise by
        the form's field definition order.
        """
        ordered_names = self._get_ordered_field_names()
        fields = []

        for fname in ordered_names:
            field = self._form.fields.get(fname)
            if not field:
                continue

            overrides = self._field_kwargs.get(fname, {})
            widget = field.widget
            bound_field = self._form[fname] if fname in self._form.fields else None

            field_ctx = {
                "name": fname,
                "label": overrides.get("label", field.label or fname.replace("_", " ").title()),
                "widget": self._detect_widget_type(widget),
                "type": self._detect_input_type(widget),
                "value": bound_field.value() if bound_field else self._form.initial.get(fname, ""),
                "help_text": overrides.get("help_text", getattr(field, "help_text", "") or ""),
                "required": field.required,
                "errors": list(bound_field.errors) if bound_field and bound_field.errors else [],
                "css_classes": overrides.get("css_classes", self._default_css(field)),
                "placeholder": overrides.get("placeholder", ""),
                "choices": self._get_choices(field),
                "has_errors": bool(bound_field and bound_field.errors),
            }
            fields.append(field_ctx)

        return fields

    def render_field(self, field_name: str) -> dict[str, Any]:
        """Generate context for a single field by name."""
        for f in self.get_fields():
            if f["name"] == field_name:
                return f
        return {"name": field_name, "widget": "text", "type": "text", "value": ""}

    def get_layout_groups(self) -> list[list[dict[str, Any]]]:
        """Group fields by layout rows.

        Returns fields organized into row groups matching the ``layout``
        parameter. Fields not in any layout group are appended as a
        final group.
        """
        fields = self.get_fields()
        field_map = {f["name"]: f for f in fields}

        if not self._layout:
            return [[f] for f in fields]

        groups = []
        seen = set()
        for row in self._layout:
            group = []
            for name in row:
                if name in field_map and name not in seen:
                    group.append(field_map[name])
                    seen.add(name)
            if group:
                groups.append(group)

        # Append remaining ungrouped fields
        remaining = [f for f in fields if f["name"] not in seen]
        if remaining:
            groups.append(remaining)

        return groups

    # ── Internal helpers ──

    def _get_ordered_field_names(self) -> list[str]:
        """Get field names in display order."""
        if self._layout:
            # Flatten layout
            names = []
            for row in self._layout:
                names.extend(row)
            # Append any fields not in layout
            for fname in self._form.fields:
                if fname not in names:
                    names.append(fname)
            return names
        return list(self._form.fields.keys())

    @staticmethod
    def _detect_widget_type(widget) -> str:
        """Detect widget type string from Django widget class."""
        name = type(widget).__name__.lower()
        widget_map = {
            "textinput": "text",
            "emailinput": "email",
            "numberinput": "number",
            "passwordinput": "password",
            "textarea": "textarea",
            "select": "select",
            "selectmultiple": "multiselect",
            "checkboxinput": "checkbox",
            "checkboxselectmultiple": "checkbox_group",
            "radioselect": "radio",
            "dateinput": "date",
            "datetimeinput": "datetime",
            "timeinput": "time",
            "fileinput": "file",
            "clearablefileinput": "file",
            "hiddeninput": "hidden",
            "urlinput": "url",
        }
        return widget_map.get(name, name.replace("input", ""))

    @staticmethod
    def _detect_input_type(widget) -> str:
        """Detect HTML input type from widget."""
        widget_type = FormTagGenerator._detect_widget_type(widget)
        if widget_type in ("text", "email", "number", "password", "date", "datetime", "time", "url", "file", "hidden"):
            return widget_type
        return "text"

    @staticmethod
    def _default_css(field) -> str:
        """Default CSS classes for a form field."""
        base = "w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition-colors"
        if field.required:
            return base
        return base + " placeholder-gray-400"

    @staticmethod
    def _get_choices(field) -> list[dict] | None:
        """Extract choices from a field if it has them."""
        if hasattr(field, "choices") and field.choices:
            return [{"value": str(v), "label": str(l)} for v, l in field.choices]
        return None
