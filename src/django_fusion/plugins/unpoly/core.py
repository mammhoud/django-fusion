"""The Unpoly request wrapper and server protocol implementation."""

from __future__ import annotations

import warnings
from functools import cached_property
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlencode

from django_fusion.comp.configuration.options import Options

from .adapter import BaseAdapter

if TYPE_CHECKING:  # pragma: no cover
    pass


def header_to_opt(header: str) -> str:
    return header[5:].lower().replace("-", "_")


def opt_to_header(opt: str) -> str:
    parts = (x.capitalize() for x in opt.split("_"))
    return f"X-Up-{'-'.join(parts)}"


def param_to_opt(param: str) -> str:
    return param[4:]


def opt_to_param(opt: str) -> str:
    return f"_up_{opt}"


class Layer:
    """Represents an layer in the Unpoly overlay stack."""

    def __init__(self, unpoly: "Unpoly", mode: str, context: dict[str, object]):
        self.unpoly = unpoly
        self.mode = mode
        self.context = context

    @property
    def is_root(self) -> bool:
        return self.mode == "root"

    @property
    def is_overlay(self) -> bool:
        return not self.is_root

    def emit(self, type: str, options: dict[str, object] | None = None) -> None:
        options = options or {}
        self.unpoly.emit(type, dict(layer="current", **options))

    def accept(self, value: object = None) -> None:
        self.unpoly.options.accept_layer = value

    def dismiss(self, value: object = None) -> None:
        self.unpoly.options.dismiss_layer = value

    def open(self, **options: object) -> None:
        self.unpoly.options.open_layer = options


class Cache:
    """Unpoly cache control helpers."""

    def __init__(self, unpoly: "Unpoly"):
        self.unpoly = unpoly
        major, minor, *_ = self.unpoly.version_info
        self._is_old = (major, minor) < (3, 11)

    def expire(self, pattern: str = "*") -> None:
        if not self._is_old and pattern == "false":
            msg = "up.cache.expire(false) is no longer supported in Unpoly 3.11."
            warnings.warn(msg, DeprecationWarning, stacklevel=1)
            return
        self.unpoly.options.expire_cache = pattern

    def evict(self, pattern: str = "*") -> None:
        self.unpoly.options.evict_cache = pattern

    def keep(self) -> None:
        if self._is_old:
            return self.expire("false")  # this is intentional
        msg = "up.cache.keep is no longer supported in Unpoly 3.11."
        warnings.warn(msg, DeprecationWarning, stacklevel=1)


class Unpoly:
    """Main entrypoint for communicating with Unpoly via HTTP headers."""

    def __init__(self, adapter: BaseAdapter):
        self.adapter = adapter

    @cached_property
    def options(self) -> Options:
        headers = dict(self.adapter.request_headers())
        params = self.adapter.request_params()

        options = {
            header_to_opt(k): v
            for k, v in headers.items()
            if k.lower().startswith("x-up-")
        }
        options.update(
            {param_to_opt(k): v for k, v in params.items() if k.startswith("_up_")}
        )
        return Options.parse(options, self.adapter)

    def __bool__(self) -> bool:
        return bool(self.options.version)

    def set_title(self, value: str) -> None:
        self.options.title = value

    def emit(self, type: str, options: dict[str, object]) -> None:
        self.options.events.append(dict(type=type, **options))

    @cached_property
    def cache(self) -> Cache:
        return Cache(self)

    @property
    def version(self) -> str:
        return self.options.version

    @property
    def version_info(self) -> list[int | str]:
        parts = self.options.version.replace("-", ".").split(".")
        return [int(part) if part.isdigit() else part for part in parts]

    @property
    def target(self) -> str:
        return self.options.server_target or self.options.target

    @target.setter
    def target(self, new_target: str) -> None:
        self.options.server_target = new_target

    @property
    def mode(self) -> str:
        return self.options.mode

    @property
    def origin_mode(self) -> str:
        return self.options.origin_mode

    @cached_property
    def origin_layer(self) -> Layer:
        return Layer(self, self.origin_mode, {})

    @property
    def context(self) -> dict[str, object]:
        return self.options.context

    @cached_property
    def layer(self) -> Layer:
        return Layer(self, self.mode or "root", self.context)

    @property
    def validate(self) -> list[str]:
        return self.options.validate.split()

    @property
    def fail_target(self) -> str:
        return self.options.server_target or self.options.fail_target

    @property
    def fail_mode(self) -> str:
        return self.options.fail_mode

    @property
    def fail_context(self) -> dict[str, object]:
        return self.options.fail_context

    @cached_property
    def fail_layer(self) -> Layer:
        return Layer(self, self.fail_mode or "root", self.fail_context)

    @property
    def needs_cookie(self) -> bool:
        return self.adapter.method != "GET" and not bool(self)

    def finalize_response(self, response: object) -> None:
        self.adapter.set_cookie(response, self.needs_cookie)

        if not self:
            return

        redirect_uri = self.adapter.redirect_uri(response)
        serialized_options = self.options.serialize(self.adapter)
        if redirect_uri:
            if "context" in serialized_options:
                serialized_options["context_diff"] = serialized_options.pop("context")
            params = {opt_to_param(k): v for k, v in serialized_options.items()}
            sep = "&" if "?" in redirect_uri else "?"
            if params:
                redirect_uri += sep + urlencode(params)
            self.adapter.set_redirect_uri(response, redirect_uri)
        else:
            loc = self.adapter.location
            if "?" in loc and "_up_" in loc:
                loc, qs = loc.split("?", 1)
                items = {
                    k: v for k, v in parse_qs(qs).items() if not k.startswith("_up_")
                }
                if items:
                    loc = f"{loc}?{urlencode(items, doseq=True)}"
                serialized_options["location"] = loc
            serialized_options["method"] = self.adapter.method
            headers = {opt_to_header(k): v for k, v in serialized_options.items()}
            self.adapter.set_headers(response, headers)
