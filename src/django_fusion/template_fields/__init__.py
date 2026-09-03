"""
django_fusion.template_fields
=============================

Sandboxed dynamic template field system.

Renders user-authored templates with inline variable placeholders
(``{{ customer.name }}``, ``{{ order.total|currency:"USD" }}``) against live
data. Templates are regex-parsed — never evaluated through Django/Jinja2 —
so server-side template injection is not possible.

Usage::

    from django_fusion.template_fields import TemplateFieldEngine

    engine = TemplateFieldEngine()
    html = engine.render(
        "Hello {{ customer.name|default:'there'}}",
        context={"customer": {"name": "Alice"}},
        allowlist=["customer"],
    )
    # "Hello Alice"

    preview = engine.preview("{{ order.total }}", {"order": {"total": 99.5}})
    # PreviewResult(html="99.5", resolved=["order.total"], unresolved=[])
"""

from django_fusion.template_fields.engine import (
    FieldReference,
    FilterSpec,
    PreviewResult,
    TemplateFieldEngine,
    ValidationIssue,
    parse_fields,
    resolve_path,
)
from django_fusion.template_fields.filters import (
    FilterRegistry,
    default_registry,
    get_filter,
    register_filter,
    sanitize_url,
)

__all__ = [
    "FieldReference",
    "FilterRegistry",
    "FilterSpec",
    "PreviewResult",
    "TemplateFieldEngine",
    "ValidationIssue",
    "default_registry",
    "get_filter",
    "parse_fields",
    "register_filter",
    "resolve_path",
    "sanitize_url",
]
