from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from django import template
from django.template.context import Context
from django.utils.safestring import SafeString, mark_safe

from django_fusion.comp.templatetags.tags.block import METADATA_ARGUMENTS, BlockNode
from django_fusion.comp.templatetags.tags.prop import PropNode

if TYPE_CHECKING:
    from .components import Component


@dataclass
class Params:
    attrs: list[Param] = field(default_factory=list)
    props: list[Param] = field(default_factory=list)
    metadata: list[Param] = field(default_factory=list)

    def render_props(self, component: Component, context: Context):
        if component.nodelist is None:
            return

        attrs_to_remove = set()

        for node in component.nodelist:
            if not isinstance(node, PropNode):
                continue

            value = Value(node.default)

            for idx, attr in enumerate(self.attrs):
                if node.name == attr.name:
                    resolved = attr.value.resolve(context)
                    if resolved is not None:
                        value = attr.value
                    attrs_to_remove.add(idx)

            self.props.append(Param(name=node.name, value=value))

        for idx in sorted(attrs_to_remove, reverse=True):
            self.attrs.pop(idx)

        return {prop.name: prop.render_prop(context) for prop in self.props}

    def render_metadata(self, context: Context) -> dict[str, Any]:
        return {param.name: param.value.resolve(context) for param in self.metadata}

    def render_attrs(self, context: Context) -> SafeString:
        rendered = " ".join(attr.render_attr(context) for attr in self.attrs)
        return mark_safe(rendered)

    @classmethod
    def from_node(cls, node: BlockNode) -> Params:
        params = [Param.from_bit(bit) for bit in node.attrs]
        metadata = [param for param in params if param.name in METADATA_ARGUMENTS]
        attrs = [param for param in params if param.name not in METADATA_ARGUMENTS]
        return cls(attrs=attrs, props=[], metadata=metadata)


@dataclass
class Param:
    name: str
    value: Value

    def render_attr(self, context: Context) -> str:
        value = self.value.resolve(context)
        if value is None:
            return ""
        name = self.name.replace("_", "-")
        if value is True:
            return name
        return f'{name}="{value}"'

    def render_prop(self, context: Context) -> str | bool | None:
        return self.value.resolve(context)

    @classmethod
    def from_bit(cls, bit: str) -> Param:
        if "=" in bit:
            name, raw_value = bit.split("=", 1)
            value = Value(raw_value.strip())
        else:
            name, value = bit, Value(True)
        return cls(name, value)


@dataclass
class Value:
    raw: str | bool | None

    def resolve(self, context: Context | dict[str, Any]) -> Any:
        match (self.raw, self.is_quoted):
            case (None, _):
                return None

            case (str(raw_str), False) if raw_str == "False":
                return None
            case (str(raw_str), False) if raw_str == "True":
                return True

            case (bool(b), _):
                return b if b else None

            case (str(raw_str), False):
                try:
                    return template.Variable(raw_str).resolve(context)
                except template.VariableDoesNotExist:
                    return raw_str

            case (_, True):
                return str(self.raw)[1:-1]

    @property
    def is_quoted(self) -> bool:
        if self.raw is None or isinstance(self.raw, bool):
            return False

        return self.raw.startswith(("'", '"')) and self.raw.endswith(self.raw[0])
