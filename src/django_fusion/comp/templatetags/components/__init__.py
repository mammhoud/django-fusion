# Component template tags package
# Re-export the top-level register so that {% load components %} works
# alongside the sub-libraries (components.card, components.menu, etc.)
from __future__ import annotations

from django import template

from ..tags import asset, block, prop, slot, var
from .menu import filter_by_url

register = template.Library()

register.tag(asset.AssetTag.CSS.value, asset.do_asset)
register.tag(asset.AssetTag.JS.value, asset.do_asset)
register.tag(block.TAG, block.do_block)
register.tag(prop.TAG, prop.do_prop)
register.tag(slot.TAG, slot.do_slot)
register.tag(var.TAG, var.do_var)
register.tag(var.END_TAG, var.do_end_var)

# Menu filter
register.filter(filter_by_url)

# Navigation tags are available via {% load components.navigation %} —
# they register on their own Library() instance in navigation.py.
# Re-registering them here would pass a callable where a template name
# string is expected (Library.inclusion_tag() signature issue).

# HISTORY: the former `{% comp_include %}` tag and its
# `include_bridge.do_comp_include` handler were removed when the include
# tag was consolidated into `{% comp %}`. The `include_bridge` module
# itself no longer exists; this note is preserved for archaeology. `IncludePathComponent`
# (in `django_fusion.comp.registry`) registers plain template paths as
# comp-name-resolvable components at startup via
# `django_fusion.comp.registry.register_default_partials()`.

# Re-export the modal_link template tag under the canonical `comp` namespace.
from ..fusion_tags import modal_link  # noqa: F401
