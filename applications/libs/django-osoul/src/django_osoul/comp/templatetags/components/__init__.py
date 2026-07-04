# Component template tags package
# Re-export the top-level register so that {% load components %} works
# alongside the sub-libraries (components.card, components.menu, etc.)
from __future__ import annotations

from django import template

from ..tags import asset, block, include_bridge, prop, slot, var

register = template.Library()

register.tag(asset.AssetTag.CSS.value, asset.do_asset)
register.tag(asset.AssetTag.JS.value, asset.do_asset)
register.tag(block.TAG, block.do_block)
register.tag(prop.TAG, prop.do_prop)
register.tag(slot.TAG, slot.do_slot)
register.tag(var.TAG, var.do_var)
register.tag(var.END_TAG, var.do_end_var)
register.tag(include_bridge.TAG, include_bridge.do_comp_include)
