"""
Forms and Tables Integration for Routes — Backward-compatible re-exports.

This module is a thin compatibility shim that forwards all imports to the
new canonical location: ``django_fusion.comp.contrib``.

Prefer importing directly from: ``django_fusion.comp.contrib``

    from django_fusion.comp.contrib.tables import TableMixin
    from django_fusion.comp.contrib.forms import FormMixin, FormTableMixin

Legacy imports continue to work: ``from django_fusion.comp.routes.forms_tables import TableMixin``.
"""

# Forward all imports to the new canonical location.
# This keeps backward compatibility — no existing code needs to change.
from django_fusion.comp.contrib.forms.mixins import FormMixin  # noqa: F401
from django_fusion.comp.contrib.tables.mixins import TableMixin  # noqa: F401
from django_fusion.comp.contrib.forms.mixins import FormTableMixin  # noqa: F401

__all__ = [
    "FormMixin",
    "TableMixin",
    "FormTableMixin",
]
