# Component template tags package
# Defines a shared Library so that {% load components %} exposes all
# component-related tags (table, pagination, search, form, modal,
# breadcrumbs, navigation, menu, etc.) while each submodule remains
# individually importable.
from __future__ import annotations

from django import template

# Shared Library instance for all component tags.
register = template.Library()

# Import submodules for side-effect registration.  The shared ``register``
# is imported by each submodule so all tags end up in one library.
from ..tags import asset, block, prop, slot, var
from . import (  # noqa: E402
    breadcrumbs,
    calendar,
    field,
    form,
    modal,
    notification,
    pagination,
    price,
    search,
    table,
)
from .breadcrumbs import breadcrumbs  # noqa: F401
from .form import form  # noqa: F401
from .modal import generate_modal, modal_link  # noqa: F401
from .pagination import fragment_pagination, pagination  # noqa: F401
from .search import search  # noqa: F401
from .table import generate_table, generate_table_rows, table  # noqa: F401

__all__ = [
    "register",
    # Core comp tags (kept here for backwards compatibility)
    "asset",
    "block",
    "prop",
    "slot",
    "var",
    # Component inclusion tags / filters exposed under {% load components %}
    "breadcrumbs",
    "form",
    "fragment_pagination",
    "generate_modal",
    "generate_table",
    "generate_table_rows",
    "modal_link",
    "pagination",
    "search",
    "table",
]

# Core comp tags are defined in the tags/ subpackage with their own
# Library instances.  Re-register their raw handlers here so
# {% load components %} exposes them too.
register.tag(asset.AssetTag.CSS.value, asset.do_asset)
register.tag(asset.AssetTag.JS.value, asset.do_asset)
register.tag(block.TAG, block.do_block)
register.tag(prop.TAG, prop.do_prop)
register.tag(slot.TAG, slot.do_slot)
register.tag(var.TAG, var.do_var)
register.tag(var.END_TAG, var.do_end_var)
