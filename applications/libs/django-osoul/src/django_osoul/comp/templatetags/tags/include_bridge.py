"""Tracking-aware replacement for Django ``{% include %}``.

Provides ``{% comp_include %}`` — a drop-in replacement for
``{% include %}`` that registers the template path in the component
registry for usage tracking, while rendering via Django's standard
``render_to_string``. This enables gradual migration planning from
plain includes to full ``{% comp %}`` components.

Limitation: this tag does NOT bridge to the full comp rendering
pipeline (slots, props, assets). For full component features, use
``{% comp "name" %}`` directly.

Usage::

    {% comp_include "partials/auth_buttons.html" user=request.user %}

    {# Migration path from legacy include: #}
    {% include "partials/auth_buttons.html" %}
    → step 1: {% comp_include "partials/auth_buttons.html" %}
    → step 2: {% comp "partials/auth_buttons.html" user=request.user %}
"""

from __future__ import annotations

from typing import final

from django import template
from django.template.base import Parser, Token
from django.template.context import Context
from django.template.exceptions import TemplateDoesNotExist
from django.utils.safestring import mark_safe

from django_osoul.comp.registry import register_include_path
from django_osoul.typing import override

TAG = "comp_include"


def do_comp_include(parser: Parser, token: Token) -> CompIncludeNode:
    """Parse ``{% comp_include "path" key=val %}`` syntax."""
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            f"{TAG} tag requires at least one argument: the template path"
        )

    path = bits[1]
    # Strip quotes from literal paths
    if (path.startswith('"') and path.endswith('"')) or (
        path.startswith("'") and path.endswith("'")
    ):
        path = path[1:-1]

    # Collect extra keyword arguments for context injection
    kwargs: dict[str, template.FilterExpression] = {}
    for bit in bits[2:]:
        if "=" in bit:
            key, val = bit.split("=", 1)
            kwargs[key] = parser.compile_filter(val)
        elif bit == "only":
            kwargs["__isolated"] = True  # type: ignore[assignment]

    return CompIncludeNode(path, kwargs)


@final
class CompIncludeNode(template.Node):
    """Render a template path, registering it in the comp registry and injecting context."""

    __slots__ = ("path", "kwargs")

    def __init__(self, path: str, kwargs: dict[str, template.FilterExpression]) -> None:
        self.path = path
        self.kwargs = kwargs

    @override
    def render(self, context: Context) -> str:
        # Resolve keyword args into the context
        resolved: dict[str, object] = {}
        isolated = False
        for key, expr in self.kwargs.items():
            if key == "__isolated":
                isolated = True
                continue
            try:
                resolved[key] = expr.resolve(context)
            except template.VariableDoesNotExist:
                resolved[key] = ""

        # Register path in comp registry for tracking
        register_include_path(self.path)

        # Render via Django's standard template system (comp registry tracks usage)
        from django.template.loader import render_to_string
        try:
            if isolated:
                return mark_safe(render_to_string(self.path, resolved))
            new_ctx = {**context.flatten(), **resolved}
            return mark_safe(render_to_string(self.path, new_ctx))
        except TemplateDoesNotExist:
            raise
