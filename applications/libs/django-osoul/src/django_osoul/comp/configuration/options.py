from __future__ import annotations

import copy
from enum import Enum
from typing import TYPE_CHECKING, cast

import attrs

if TYPE_CHECKING:  # pragma: no cover
    from .adapters import BaseAdapter


class _Sentinel(Enum):
    SENTINEL = 0


@attrs.define(kw_only=True)
class Options:
    # mostly request options
    version: str = ""
    target: str = ""
    mode: str = ""
    context: dict[str, object] = attrs.field(factory=dict)
    fail_target: str = ""
    fail_mode: str = ""
    fail_context: dict[str, object] = attrs.field(factory=dict)
    origin_mode: str = ""
    validate: str = ""

    # internal params
    server_target: str = attrs.field(init=False, default="")
    initial_context: dict[str, object] = attrs.field(init=False)

    # explicit response options
    title: str = ""
    expire_cache: str = ""
    evict_cache: str = ""
    accept_layer: object | _Sentinel = _Sentinel.SENTINEL
    dismiss_layer: object | _Sentinel = _Sentinel.SENTINEL
    open_layer: object | _Sentinel = _Sentinel.SENTINEL
    events: list[dict[str, object]] = attrs.field(factory=list)

    def __attrs_post_init__(self) -> None:
        self.initial_context = copy.deepcopy(self.context)

    @property
    def context_diff(self) -> dict[str, object]:
        old = self.initial_context
        new = self.context
        old_keys = set(old)
        new_keys = set(new)
        result: dict[str, object] = {}
        for key in old_keys - new_keys:
            result[key] = None
        for key in new_keys - old_keys:
            result[key] = new[key]
        for key in new_keys & old_keys:
            if old[key] != new[key]:
                result[key] = new[key]
        return result

    @classmethod
    def parse(cls, options: dict[str, str], adapter: BaseAdapter) -> Options:
        parsed_options = cast(dict[str, object], options)
        for opt in (
            "events",
            "context",
            "context_diff",
            "fail_context",
            "dismiss_layer",
            "accept_layer",
            "title",
        ):
            if opt in options:
                decoded: object = adapter.deserialize_data(options[opt])
                if decoded is None:
                    if opt in {"context", "fail_context", "context_diff"}:
                        decoded = {}
                    elif opt == "events":
                        decoded = []
                parsed_options[opt] = decoded
        context_diff = cast(dict[str, object], parsed_options.pop("context_diff", {}))

        opts = cls(**parsed_options)  # type: ignore [reportGeneralTypeIssues,arg-type]
        # Apply the passed context diff
        if context_diff:
            for k, v in context_diff.items():
                if v is None and k in opts.context:
                    del opts.context[k]
                else:
                    opts.context[k] = v
        return opts

    def serialize(self, adapter: BaseAdapter) -> dict[str, str]:
        serialized_options: dict[str, str] = {}

        for key in ("events", "title"):
            if value := getattr(self, key):
                serialized_options[key] = adapter.serialize_data(value)
        for key in ("accept_layer", "dismiss_layer", "open_layer"):
            value = getattr(self, key)
            if value != _Sentinel.SENTINEL:
                serialized_options[key] = adapter.serialize_data(getattr(self, key))

        if self.expire_cache:
            serialized_options["expire_cache"] = self.expire_cache
        if self.evict_cache:
            serialized_options["evict_cache"] = self.evict_cache

        # Update with new target, if it changed
        if self.server_target and self.server_target != self.target:
            serialized_options["target"] = self.server_target

        # Update with context changes, see https://unpoly.com/X-Up-Context
        diff = self.context_diff
        if diff:
            serialized_options["context"] = adapter.serialize_data(diff)

        return serialized_options
