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

    # Accept both documented forms:
    #   {% prop name="default" %}      — default attached to the name
    #   {% prop name default="v" %}    — kwarg-style default (used by LMS
    #                                     component templates). Previously the
    #                                     ``default=`` bit was silently
    #                                     dropped, so the prop default always
    #                                     resolved to None.
    prop = bits.pop(0)
    name = prop
    default = None

    if "=" in prop:
        name, _, default = prop.partition("=")

    for bit in bits:
        if bit.startswith("default="):
            default = bit.split("=", 1)[1]
            break

    return PropNode(name, default, [])


@final
class PropNode(template.Node):
    def __init__(self, name: str, default: str | None, attrs: TagBits):
        self.name = name
        self.default = default
        self.attrs = attrs

    @override
    def render(self, context: Context) -> str:
        return ""
