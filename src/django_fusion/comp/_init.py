from __future__ import annotations

import itertools
from collections import defaultdict
from collections.abc import Generator, Iterable, Set as AbstractSet
from dataclasses import dataclass, field
from hashlib import md5
from pathlib import Path
from threading import Lock
from typing import Any

from django.conf import settings
from django.template.backends.django import Template as DjangoTemplate
from django.template.base import Node, NodeList, TextNode
from django.template.context import Context
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import select_template

from django_fusion.config.conf import _settings
from django_fusion.config.params import Param, Params, Value
from django_fusion.plugins.manager import pm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_fusion.config.staticfiles import Asset, AssetType
from django_fusion.comp.loader.templates import (
    find_components_in_template,
    get_component_directories,
    get_template_names,
)
from django_fusion.comp.templatetags.tags.block import BlockNode, validate_fragment_name
from django_fusion.comp.templatetags.tags.slot import DEFAULT_SLOT, SlotNode


@dataclass(frozen=True, slots=True)
class Component:
    name: str
    # ``template`` is ``DjangoTemplate`` for the common path-style case
    # (resolved at include time). ``registry._LazyIncludeTemplate`` is
    # the duck-typed alternative returned by
    # ``IncludePathComponent.from_include_path``; it defers
    # ``select_template`` until first render so partials that depend on
    # tag libraries unavailable in the current settings (e.g.
    # wagtailimages_tags) don't blow up the registry at import time.
    template: DjangoTemplate | "_LazyIncludeTemplate"
    assets: AbstractSet[Asset] = field(default_factory=frozenset)

    @property
    def identity(self) -> str:
        """Stable registry identity used by props, metadata, and assets."""
        return self.name

    def get_asset(self, asset_filename: str) -> Asset | None:
        for asset in self.assets:
            if asset.path.name == asset_filename:
                return asset
        return None

    def get_bound_component(self, node: BlockNode):
        params = Params.from_node(node)
        return BoundComponent(component=self, params=params, nodelist=node.nodelist)

    @property
    def data_attribute_name(self):
        return self.name.replace(".", "-")

    @property
    def id(self):
        normalized_source = "".join(self.source.split())
        hashed = md5(f"{self.name}:{self.path}:{normalized_source}".encode()).hexdigest()
        return hashed[:7]

    @property
    def nodelist(self):
        return self.template.template.nodelist

    @property
    def path(self):
        return self.template.template.origin.name

    @property
    def source(self):
        return self.template.template.source

    @classmethod
    def from_abs_path(cls, path: Path) -> Component:
        template = select_template([str(path)])
        return cls.from_template(template)

    @classmethod
    def from_name(cls, name: str) -> Component:
        template_names = (
            [name] if "/" in name or name.endswith(".html") else get_template_names(name)
        )
        template = select_template(template_names)
        return cls.from_template(template)

    @classmethod
    def from_template(cls, template: DjangoTemplate) -> Component:
        template_path = Path(template.template.origin.name)

        for component_dir in get_component_directories():
            try:
                relative_path = template_path.relative_to(component_dir)
                name = str(relative_path.with_suffix("")).replace("/", ".")
                break
            except ValueError:
                continue
        else:
            name = template_path.stem

        assets: list[Iterable[Asset]] = pm.hook.collect_component_assets(
            template_path=Path(template.template.origin.name)
        )

        return cls(name=name, template=template, assets=frozenset(itertools.chain(*assets)))


class SequenceGenerator:
    _instance: SequenceGenerator | None = None
    _lock: Lock = Lock()
    _counters: dict[str, int]

    def __init__(self) -> None:
        if not hasattr(self, "_counters"):
            self._counters = {}

    def __new__(cls) -> SequenceGenerator:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def next(self, component: Component) -> int:
        with self._lock:
            current = self._counters.get(component.id, 0) + 1
            self._counters[component.id] = current
        return current


@dataclass(frozen=True, slots=True)
class ComponentRenderMetadata:
    """Immutable metadata linking one render to its page, props, and assets."""

    name: str
    source: Any = None
    requested_by: Any = None
    fragment_name: str | None = None
    page_path: str | None = None
    props: tuple[tuple[str, str], ...] = ()
    assets: tuple[str, ...] = ()


@dataclass
class BoundComponent:
    component: Component
    params: Params
    nodelist: NodeList | None
    _sequence: SequenceGenerator = field(default_factory=SequenceGenerator)

    def render(self, context: Context):
        metadata_values = self.params.render_metadata(context)
        validate_fragment_name(metadata_values.get("fragment_name"))

        props = self.params.render_props(self.component, context)
        extra_attrs: tuple[Param, ...] = ()
        if _settings.ENABLE_BLOCK_ATTRS:
            extra_attrs = (
                Param(
                    f"data-block-{self.component.data_attribute_name}",
                    Value(True),
                ),
                Param("data-block-id", Value(f'"{self.component.id}-{self.id}"')),
            )
        attrs = self.params.render_attrs(
            context,
            exclude=set(props),
            extra=extra_attrs,
        )

        request = context.get("request")
        page = context.get("page") or context.get("page_obj")
        page_path = getattr(request, "path", None) if request is not None else None
        if page_path is None:
            page_path = getattr(page, "url", None)
        render_metadata = ComponentRenderMetadata(
            name=self.component.name,
            source=metadata_values.get("source"),
            requested_by=metadata_values.get("requested_by"),
            fragment_name=metadata_values.get("fragment_name"),
            page_path=page_path,
            props=tuple(sorted((name, repr(value)) for name, value in props.items())),
            assets=tuple(sorted(str(asset.path) for asset in self.component.assets)),
        )
        components.record_render(render_metadata)
        slots = self.fill_slots(context)

        with context.push(
            **{
                "attrs": attrs,
                "props": props,
                "slot": slots.get(DEFAULT_SLOT),
                "slots": slots,
                "vars": {},
                "component": render_metadata,
                "component_context": render_metadata,
            }
        ):
            return self.component.template.template.render(context)

    def fill_slots(self, context: Context):
        if self.nodelist is None:
            return {
                DEFAULT_SLOT: None,
            }

        slot_nodes = {node.name: node for node in self.nodelist if isinstance(node, SlotNode)}
        default_nodes = NodeList([node for node in self.nodelist if not isinstance(node, SlotNode)])

        slots: dict[str, Node | NodeList] = {
            DEFAULT_SLOT: default_nodes,
            **slot_nodes,
        }

        if not slots[DEFAULT_SLOT] and "slot" in context:
            slots[DEFAULT_SLOT] = TextNode(context["slot"])

        return {name: node.render(context) for name, node in slots.items() if node}

    @property
    def id(self):
        return str(self._sequence.next(self.component))


class ComponentRegistry:
    def __init__(self):
        self._component_usage: dict[str, set[Path]] = defaultdict(set)
        self._components: dict[str, Component] = {}
        self._template_usage: dict[Path, set[str]] = defaultdict(set)
        self._render_history: list[ComponentRenderMetadata] = []
        self._ambiguous_aliases: set[str] = set()

    def reset(self) -> None:
        """Reset the registry, used for testing."""
        self._component_usage = defaultdict(set)
        self._components = {}
        self._template_usage = defaultdict(set)
        self._render_history = []
        self._ambiguous_aliases = set()

    def register_alias(self, alias: str, component: Component) -> bool:
        """Register a unique alias or quarantine an ambiguous alias.

        Bare aliases are an ergonomic optimization for a single include
        path, not a second identity. If multiple paths share the same stem,
        the alias is removed and marked ambiguous so registration order can
        never change which component it resolves to.
        """
        if not alias or alias in self._ambiguous_aliases:
            return False

        existing = self._components.get(alias)
        if existing is None:
            self._components[alias] = component
            self._component_usage.setdefault(alias, set())
            return True
        if existing is component:
            return True

        self._components.pop(alias, None)
        self._ambiguous_aliases.add(alias)
        return False

    def is_ambiguous_alias(self, alias: str) -> bool:
        """Return whether a bare alias has multiple canonical paths."""
        return alias in self._ambiguous_aliases

    def record_render(self, metadata: ComponentRenderMetadata) -> None:
        self._render_history.append(metadata)
        
        # Cache render event if Redis is available
        try:
            from django_fusion.comp.cache import get_component_map_cache
            cache = get_component_map_cache()
            cache.record_render(metadata.name)
        except Exception as e:
            # Silently fail if caching doesn't work
            pass

    def get_render_history(self) -> tuple[ComponentRenderMetadata, ...]:
        return tuple(self._render_history)

    def register(self, component: Component, *, name: str | None = None) -> Component:
        """Register a component once and return the canonical instance."""
        key = name or component.identity
        existing = self._components.get(key)
        if existing is not None:
            return existing
        self._components[key] = component
        self._component_usage.setdefault(key, set())
        return component

    def get_assets(self, asset_type: AssetType | None = None) -> frozenset[Asset]:
        return frozenset(
            asset
            for component in self._components.values()
            for asset in component.assets
            if asset_type is None or asset.type == asset_type
        )

    def get_component(self, name: str) -> Component:
        # Component identity is stable for the lifetime of this registry,
        # including DEBUG mode. Reset explicitly when development needs a
        # fresh template registry; do not create duplicate nodes per render.
        if name in self._components:
            return self._components[name]
        if name in self._ambiguous_aliases:
            raise TemplateDoesNotExist(
                f"Ambiguous component alias {name!r}; use the full template path"
            )

        # Consult the external path cache only as a hint. The in-memory
        # canonical instance above remains the source of truth.
        try:
            from django_fusion.comp.cache import get_component_map_cache
            get_component_map_cache().get_component(name)
        except Exception:
            pass

        # Path-style names (containing / or ending in .html) are
        # resolved differently depending on whether they live under a
        # recognised component directory:
        #
        # * UNDER a component dir (e.g. "components/static.html"):
        #   delegate to ``Component.from_name`` which derives the
        #   canonical name relative to the component dir root
        #   ("static").
        #
        # * NOT under a component dir (e.g. "partials/auth_buttons.html"):
        #   use ``IncludePathComponent.from_include_path`` which
        #   preserves the full include-path verbatim as the component
        #   name, making render-history introspection match the string
        #   the author typed in ``{% comp "partials/auth_buttons.html" %}``.
        if name.endswith(".html") or "/" in name:
            component_dirs = get_component_directories()
            is_under_comp_dir = any(
                name.startswith(f"{d.name}/") for d in component_dirs
            )
            if is_under_comp_dir:
                component = Component.from_name(name)
            else:
                from django_fusion.comp.registry import IncludePathComponent

                component = IncludePathComponent.from_include_path(name)
        else:
            component = Component.from_name(name)

        component = self.register(component, name=name)
        
        # Cache the resolved component
        try:
            from django_fusion.comp.cache import get_component_map_cache
            cache = get_component_map_cache()
            cache.set_component(name, self._components[name].path)
        except Exception:
            pass  # Silently fail if caching doesn't work
        
        return component

    def get_component_names_used_in_template(self, template_path: str | Path) -> set[str]:
        """Get names of components used in a template."""

        path = Path(template_path)

        if path in self._template_usage:
            return self._template_usage[path]

        components = find_components_in_template(template_path)

        self._template_usage[path] = components
        for component_name in components:
            self._component_usage[component_name].add(path)

        return components

    def get_component_usage(self, template_path: str | Path) -> Generator[Component, Any, None]:
        """Get components used in a template."""
        for component_name in self.get_component_names_used_in_template(template_path):
            yield self.get_component(component_name)


components = ComponentRegistry()
