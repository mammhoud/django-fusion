# pyright: reportAny=false
from __future__ import annotations

from typing import final

from django import template
from django.template.base import Parser, Token
from django.template.context import Context

from django_fusion.typing import TagBits, override

TAG = "prop"


def do_prop(_parser: Parser, token: Token) -> PropNode:
    _tag, *bits = token.split_contents()
    if not bits:
        msg = f"{TAG} tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)

    prop = bits.pop(0)

    try:
        name, default = prop.split("=")
    except ValueError:
        name = prop
        default = None

    return PropNode(name, default, bits)


@final
class PropNode(template.Node):
    def __init__(self, name: str, default: str | None, attrs: TagBits):
        self.name = name
        self.default = default
        self.attrs = attrs

    @override
    def render(self, context: Context) -> str:
        return ""
