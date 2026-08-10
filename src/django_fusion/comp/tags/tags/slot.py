# pyright: reportAny=false
from __future__ import annotations

from typing import cast, final

from django import template
from django.template.base import Node, NodeList, Parser, Token
from django.template.context import Context
from django.utils.safestring import SafeString

from django_fusion.typing import override

TAG = "slot"
END_TAG = "endslot"

DEFAULT_SLOT = "default"


def do_slot(parser: Parser, token: Token) -> SlotNode:
    _tag, *bits = token.split_contents()
    if len(bits) > 1:
        msg = f"{TAG} tag requires either one or no arguments"
        raise template.TemplateSyntaxError(msg)

    if len(bits) == 0:
        name = DEFAULT_SLOT
    else:
        name = bits[0]
        if name.startswith("name="):
            _, name = name.split("=")
        name = name.strip("'\"")

    nodelist = parser.parse((END_TAG,))
    parser.delete_first_token()

    return SlotNode(name, nodelist)


@final
class SlotNode(template.Node):
    def __init__(self, name: str, nodelist: NodeList):
        self.name = name
        self.nodelist = nodelist

    @override
    def render(self, context: Context) -> SafeString:
        slots = context.get("slots")

        if not slots or not isinstance(slots, dict):
            return self.nodelist.render(context)

        slots_dict = cast(dict[str, Node | NodeList | str], slots)
        slot_content = slots_dict.get(self.name)

        # Caller provided no content for this slot → render this node's own
        # fallback body exactly once.
        if slot_content is None:
            return self.nodelist.render(context)

        # Raw nodelist/node from ``BoundComponent.fill_slots`` — render it
        # once with the current context. Never re-parse already-rendered
        # output as a fresh template (that double-renders any ``{{ }}`` /
        # ``{% %}`` sequences in the caller's content).
        if isinstance(slot_content, Node):
            return slot_content.render(context)
        if isinstance(slot_content, NodeList):
            return slot_content.render(context)

        # Legacy / external callers may still pass a pre-rendered string;
        # emit it verbatim (it is already final output).
        return cast(str, slot_content)
