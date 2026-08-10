"""Pure handlers for the django-fusion interactive designer.

Handlers return JSON-serializable dictionaries and deliberately do not perform
filesystem writes, database writes, arbitrary template compilation, or task
execution. They are suitable for MCP adapters and direct unit tests.
"""

from __future__ import annotations

import re
from typing import Any

from django.template import Context

from django_fusion.comp._init import components

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_MAX_ITEMS = 50
_MAX_TEXT = 160


_WAGTAIL_FIELD_TYPES: dict[str, dict[str, Any]] = {
    "char": {
        "class": "CharField",
        "import": "from django.db import models",
        "kwargs": {"max_length": 255, "blank": True},
        "description": "Short text input stored in a Django model field.",
    },
    "text": {
        "class": "TextField",
        "import": "from django.db import models",
        "kwargs": {"blank": True},
        "description": "Long text input stored in a Django model field.",
    },
    "rich_text": {
        "class": "RichTextField",
        "import": "from wagtail.fields import RichTextField",
        "kwargs": {"blank": True},
        "description": "Wagtail rich-text content field.",
    },
    "image": {
        "class": "ForeignKey",
        "import": "from django.db import models",
        "kwargs": {"to": "wagtailimages.Image", "on_delete": "models.SET_NULL", "null": True, "blank": True},
        "description": "Optional Wagtail image relationship.",
    },
    "choice": {
        "class": "ChoiceBlock",
        "import": "from wagtail.blocks import ChoiceBlock",
        "kwargs": {"choices": []},
        "description": "Editor-selectable value in a Wagtail StreamField block.",
    },
    "struct": {
        "class": "StructBlock",
        "import": "from wagtail.blocks import StructBlock",
        "kwargs": {"children": {}},
        "description": "Composite Wagtail block containing named child blocks.",
    },
    "stream": {
        "class": "StreamField",
        "import": "from wagtail.fields import StreamField",
        "kwargs": {"block_types": [], "blank": True, "use_json_field": True},
        "description": "Ordered Wagtail content stream made from approved block types.",
    },
}


def _text(value: Any, *, default: str = "", limit: int = _MAX_TEXT) -> str:
    value = default if value is None else str(value)
    return value.strip()[:limit]


def _identifier(value: Any, *, label: str) -> str:
    value = _text(value)
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"{label} must be a Python identifier")
    return value


def _json_value(value: Any) -> Any:
    """Validate and return JSON-compatible values for preview context."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    raise ValueError("props must contain only JSON-compatible values")


def _bounded_list(value: Any, *, label: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    if len(value) > _MAX_ITEMS:
        raise ValueError(f"{label} may contain at most {_MAX_ITEMS} items")
    return value


def _python_literal(value: Any) -> str:
    """Render only JSON-like values as a deterministic Python literal."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(_python_literal(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(
            f"{_python_literal(str(key))}: {_python_literal(item)}"
            for key, item in value.items()
        ) + "}"
    raise ValueError("Values must be JSON-compatible")


def designer_component_catalog(query: str = "", limit: int = 50) -> dict[str, Any]:
    """List registered components and optionally filter by name/path."""
    try:
        limit = max(1, min(int(limit), _MAX_ITEMS))
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc
    needle = _text(query, limit=80).lower()
    items = []
    registered = components.registered_components()
    for name in sorted(registered):
        if needle and needle not in name.lower():
            continue
        component = registered[name]
        items.append(
            {
                "name": name,
                "identity": component.identity,
                "template": name if name.endswith(".html") else None,
                "has_assets": bool(component.assets),
                "ambiguous_alias": components.is_ambiguous_alias(name),
            }
        )
        if len(items) >= limit:
            break
    return {"components": items, "count": len(items), "query": needle}


def designer_wagtail_field(
    field_type: str,
    name: str,
    label: str = "",
    required: bool = False,
    help_text: str = "",
    choices: list[Any] | None = None,
) -> dict[str, Any]:
    """Return a validated Wagtail/Django field or block recommendation."""
    field_type = _text(field_type, limit=40).lower()
    spec = _WAGTAIL_FIELD_TYPES.get(field_type)
    if spec is None:
        raise ValueError(f"Unsupported field_type; choose one of {sorted(_WAGTAIL_FIELD_TYPES)}")
    name = _identifier(name, label="name")
    choices = _bounded_list(choices, label="choices")
    if field_type == "choice" and not choices:
        raise ValueError("choices is required for a choice field")
    kwargs = dict(spec["kwargs"])
    if field_type == "choice":
        kwargs["choices"] = choices
    if field_type in {"char", "text", "rich_text", "image", "stream"}:
        kwargs["blank"] = not required
    return {
        "field": {
            "name": name,
            "label": _text(label, default=name.replace("_", " ").title()),
            "type": field_type,
            "class": spec["class"],
            "required": bool(required),
            "help_text": _text(help_text),
            "kwargs": kwargs,
        },
        "recommendation": spec["description"],
        "write_required": True,
        "next_step": "Review this draft, then add it to an owned model or StreamField block in the project.",
    }


def designer_form_scaffold(
    class_name: str,
    fields: list[dict[str, Any]],
    base: str = "BaseStyledForm",
    style_framework: str = "bootstrap",
) -> dict[str, Any]:
    """Generate a review-only Django form scaffold from field metadata."""
    class_name = _identifier(class_name, label="class_name")
    base = _identifier(base, label="base")
    if base != "BaseStyledForm":
        raise ValueError("base must be the approved BaseStyledForm class")
    if style_framework not in {"bootstrap", "tailwind"}:
        raise ValueError("style_framework must be bootstrap or tailwind")
    fields = _bounded_list(fields, label="fields")
    lines = [
        "from django import forms",
        "from django_fusion.fragments.forms.forms import BaseStyledForm",
        "",
        f"class {class_name}(BaseStyledForm, forms.Form):",
        f"    \"\"\"Review-only scaffold generated for {style_framework}.\"\"\"",
    ]
    if not fields:
        lines.append("    pass")
    for field in fields:
        if not isinstance(field, dict):
            raise ValueError("each form field must be an object")
        name = _identifier(field.get("name"), label="field name")
        field_type = _text(field.get("type"), default="char", limit=30)
        django_class = {
            "char": "CharField",
            "email": "EmailField",
            "text": "CharField",
            "integer": "IntegerField",
            "boolean": "BooleanField",
            "url": "URLField",
        }.get(field_type)
        if django_class is None:
            raise ValueError(f"Unsupported form field type: {field_type}")
        kwargs: dict[str, Any] = {"required": bool(field.get("required", False))}
        if field.get("label"):
            kwargs["label"] = _text(field["label"])
        if field_type == "text":
            kwargs["widget"] = "forms.Textarea"
        if field.get("help_text"):
            kwargs["help_text"] = _text(field["help_text"])
        rendered_kwargs = ", ".join(
            f"{key}={value if key == 'widget' else _python_literal(value)}"
            for key, value in kwargs.items()
        )
        lines.append(f"    {name} = forms.{django_class}({rendered_kwargs})")
    return {
        "kind": "django_form",
        "class_name": class_name,
        "style_framework": style_framework,
        "code": "\n".join(lines) + "\n",
        "write_required": True,
        "recommendations": [
            "Review field validation and permissions before adding this class.",
            "Use the project-owned template/component for rendering and HTMX behavior.",
        ],
    }


def designer_table_scaffold(
    class_name: str,
    columns: list[dict[str, Any]],
    base: str = "BaseTable",
) -> dict[str, Any]:
    """Generate a review-only django-tables2 scaffold."""
    class_name = _identifier(class_name, label="class_name")
    base = _identifier(base, label="base")
    if base != "BaseTable":
        raise ValueError("base must be the approved BaseTable class")
    columns = _bounded_list(columns, label="columns")
    lines = [
        "import django_tables2 as tables",
        "from django_fusion.fragments.tables.table import BaseTable",
        "",
        f"class {class_name}({base}):",
    ]
    if not columns:
        lines.append("    pass")
    for column in columns:
        if not isinstance(column, dict):
            raise ValueError("each table column must be an object")
        name = _identifier(column.get("name"), label="column name")
        kwargs = []
        if column.get("label"):
            kwargs.append(f"verbose_name={_python_literal(_text(column['label']))}")
        if "orderable" in column:
            kwargs.append(f"orderable={bool(column['orderable'])!r}")
        lines.append(f"    {name} = tables.Column({', '.join(kwargs)})")
    return {
        "kind": "django_table",
        "class_name": class_name,
        "code": "\n".join(lines) + "\n",
        "write_required": True,
        "recommendations": [
            "Keep queryset filtering and authorization in the project-owned view.",
            "Expose only columns appropriate for the current user's permissions.",
        ],
    }


def designer_validate(draft: dict[str, Any]) -> dict[str, Any]:
    """Validate a designer draft without applying it."""
    if not isinstance(draft, dict):
        raise ValueError("draft must be an object")
    kind = _text(draft.get("kind"), limit=40)
    if kind == "django_form":
        result = designer_form_scaffold(
            draft.get("class_name", "GeneratedForm"),
            draft.get("fields", []),
            draft.get("base", "BaseStyledForm"),
            draft.get("style_framework", "bootstrap"),
        )
    elif kind == "django_table":
        result = designer_table_scaffold(
            draft.get("class_name", "GeneratedTable"),
            draft.get("columns", []),
            draft.get("base", "BaseTable"),
        )
    elif kind == "wagtail_field":
        field_draft = {key: value for key, value in draft.items() if key != "kind"}
        result = designer_wagtail_field(**field_draft)
    else:
        raise ValueError("kind must be django_form, django_table, or wagtail_field")
    return {"valid": True, "kind": kind, "draft": result, "applied": False}


def designer_preview(name: str, props: dict[str, Any] | None = None, max_chars: int = 20_000) -> dict[str, Any]:
    """Render one already-registered component with JSON props only."""
    name = _text(name, limit=200)
    registered = components.registered_components()
    if not name or name not in registered:
        raise ValueError("name must identify a registered component")
    if components.is_ambiguous_alias(name):
        raise ValueError("Use the full template path for an ambiguous component alias")
    if props is not None and not isinstance(props, dict):
        raise ValueError("props must be an object")
    try:
        max_chars = max(100, min(int(max_chars), 50_000))
    except (TypeError, ValueError) as exc:
        raise ValueError("max_chars must be an integer") from exc
    safe_props = _json_value(dict(props or {}))
    component = registered[name]
    html = component.template.template.render(Context({"props": safe_props, **safe_props}))
    truncated = len(html) > max_chars
    return {
        "name": name,
        "html": html[:max_chars],
        "truncated": truncated,
        "max_chars": max_chars,
        "write_required": False,
        "security_note": "Preview accepts a registered component name and JSON props; raw template source is not accepted.",
    }
