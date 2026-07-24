# pyright: reportAny=false
from __future__ import annotations

import re
from typing import final

from django import template
from django.template.base import NodeList, Parser, Token
from django.template.context import Context

from django_fusion.typing import TagBits, override

TAG = "comp"
END_TAG = "endcomp"
METADATA_ARGUMENTS = {"source", "requested_by", "fragment_name"}
FRAGMENT_NAME_ALIASES = {"fragment", "fragment_slug", "fragment_key"}
FRAGMENT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def validate_argument_name(bit: str) -> None:
    name = bit.split("=", 1)[0]
    if name in FRAGMENT_NAME_ALIASES:
        msg = (
            "Use fragment_name for component fragment identifiers; "
            f"{name!r} is not supported."
        )
        raise template.TemplateSyntaxError(msg)


def validate_fragment_name(value: object) -> None:
    if value in (None, ""):
        return
    if not isinstance(value, str) or not FRAGMENT_NAME_PATTERN.fullmatch(value):
        msg = (
            "fragment_name must start with a lowercase letter and contain only "
            "lowercase letters, numbers, and underscores."
        )
        raise template.TemplateSyntaxError(msg)


def do_block(parser: Parser, token: Token) -> BlockNode:
    _tag, *bits = token.split_contents()
    if not bits:
        msg = f"{TAG} tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)

    name = bits.pop(0)
    attrs: TagBits = []
    isolated_context = False
    self_closing = False

    for bit in bits:
        match bit:  # type: ignore
            case "only":
                isolated_context = True
            case "/":
                self_closing = True
                continue
            case _:
                validate_argument_name(bit)
                attrs.append(bit)

    nodelist = parse_nodelist(parser, self_closing=self_closing)
    return BlockNode(name, attrs, nodelist, isolated_context)


def parse_nodelist(parser: Parser, *, self_closing: bool = False) -> NodeList | None:
    # Self-closing or standalone tag. Standalone form supports:
    # {% comp "components/card.html" title="Hello" %}
    if self_closing or not has_end_tag(parser):
        return None

    nodelist = parser.parse((END_TAG,))
    parser.delete_first_token()
    return nodelist


def has_end_tag(parser: Parser) -> bool:
    for token in reversed(parser.tokens):
        if token.contents.split(maxsplit=1)[0] == END_TAG:
            return True
    return False


@final
class BlockNode(template.Node):
    def __init__(
        self,
        name: str,
        attrs: TagBits,
        nodelist: NodeList | None,
        isolated_context: bool = False,
    ) -> None:
        self.name = name
        self.attrs = attrs
        self.nodelist = nodelist
        self.isolated_context = isolated_context

    @override
    def render(self, context: Context) -> str:
        from django_fusion.comp.fragment._init import components

        component_name = self.get_component_name(context)
        component = components.get_component(component_name)
        bound_component = component.get_bound_component(node=self)

        if self.isolated_context:
            return bound_component.render(context.new())
        else:
            return bound_component.render(context)

    def get_component_name(self, context: Context) -> str:
        try:
            name = template.Variable(self.name).resolve(context)
        except template.VariableDoesNotExist:
            name = self.name
        return name
