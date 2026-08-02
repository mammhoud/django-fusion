# pyright: reportAny=false
from __future__ import annotations

from typing import final

from django import template
from django.conf import settings
from django.template.base import Parser, Token
from django.template.context import Context

from django_fusion.config.asset_tag import AssetTag
from django_fusion.config.manifest import load_asset_manifest, normalize_path


def do_asset(_parser: Parser, token: Token) -> AssetNode:
    bits = token.split_contents()
    if len(bits) < 1:
        msg = "block:assets tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)
    tag_name = bits[0]
    asset_tag = AssetTag(tag_name)
    return AssetNode(asset_tag)


@final
class AssetNode(template.Node):
    def __init__(self, asset_tag: AssetTag):
        self.asset_tag = asset_tag

    def render(self, context: Context) -> str:
        from django_fusion.comp._init import components
        from django_fusion.config.staticfiles import Asset, get_component_assets

        template = getattr(context, "template", None)
        if not template:
            return ""

        template_path = template.origin.name

        used_components = []

        # Only use manifest in production mode
        if not settings.DEBUG:
            manifest = load_asset_manifest()
            normalized_path = normalize_path(template_path)
            if manifest and normalized_path in manifest:
                component_names = manifest[normalized_path]
                used_components = [
                    components.get_component(name) for name in component_names
                ]

        # If we're in development or there was no manifest data, use registry
        if not used_components:
            used_components = list(components.get_component_usage(template_path))

        assets: set[Asset] = set()
        for component in used_components:
            component_assets = get_component_assets(component)
            assets.update(
                asset for asset in component_assets if asset.type.tag == self.asset_tag
            )

        if not assets:
            return ""

        rendered = [asset.render() for asset in sorted(assets, key=lambda a: a.path)]
        return "\n".join(rendered)
