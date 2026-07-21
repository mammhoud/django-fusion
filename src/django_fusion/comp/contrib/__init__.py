"""
django_fusion.comp.contrib — Forms & Tables Integration.

Unified, dependency-free framework for form handling and table rendering
in routable components. Provides enhanced mixins with ORM data support,
auto row generation, and form tag generation.

Canonical imports::

    from django_fusion.comp.contrib.tables import TableMixin, RowGenerator
    from django_fusion.comp.contrib.forms import FormMixin, FormTagGenerator, FormTableMixin

Legacy imports continue to work via ``django_fusion.comp.routes.forms_tables``
which forwards to this package.
"""

from django_fusion.comp.contrib.forms import FormMixin, FormTableMixin, FormTagGenerator
from django_fusion.comp.contrib.tables import RowGenerator, TableMixin

__all__ = [
    # Tables
    "TableMixin",
    "RowGenerator",
    # Forms
    "FormMixin",
    "FormTableMixin",
    "FormTagGenerator",
]
