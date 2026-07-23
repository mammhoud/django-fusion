"""
The module :mod:`unpoly.up` exposes the main :class:`.Unpoly` class which is used to
communicate with Unpoly via HTTP headers. All the information of the
`Unpoly server protocol <https://unpoly.com/up.protocol>`_ is exposed and easily
accessable.

An example usage could look like this (`request.up` is enabled via the
:ref:`Django Integration <django>`):

.. code-block:: python

    def create_user(request):
        # Set a nice <title> for unpoly
        request.up.set_title("Create user | MyDomain.com")
        if request.method == "POST":
            form = UserForm(request.POST)
        else:
            form = UserForm()
        # Do not save the form if unpoly is just trying
        # to validate a form field
        if form.is_valid() and not request.up.validate:
            instance = form.save()
            # Tell unpoly that the user was created successfully
            request.up.emit("user:created", {"id": instance.pk})
            # and also close the layer
            request.up.layer.accept()
        return render(request, "template.html", {"form": form})
"""

from __future__ import annotations

import warnings
from functools import cached_property
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlencode

from django_fusion.comp.configuration.options import Options

if TYPE_CHECKING:  # pragma: no cover
    from .adapters import BaseAdapter


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
    def __init__(self, unpoly: Unpoly, mode: str, context: dict[str, object]):
        self.unpoly = unpoly
        self.mode = mode  #: Current layer mode (`X-Up[-Fail]-Mode`).
        self.context = context  #: Current layer context (`X-Up[-Fail]-Context`).

    @property
    def is_root(self) -> bool:
        """Returns whether this is the root layer."""
        return self.mode == "root"

    @property
    def is_overlay(self) -> bool:
        """Returns whether this is an overlay layer."""
        return not self.is_root

    def emit(self, type: str, options: dict[str, object] | None = None) -> None:
        """Emit events to the frontend (`X-Up-Events`).

        Similar to :meth:`.Unpoly.emit` but emits on the current layer.
        """
        options = options or {}
        self.unpoly.emit(type, dict(layer="current", **options))

    def accept(self, value: object = None) -> None:
        """Accept the current layer (`X-Up-Accept-Layer`).

        An optional value can be provided to be passed back to the client."""
        # assert self.is_overlay -- the client simply ignores this on the root layer
        self.unpoly.options.accept_layer = value

    def dismiss(self, value: object = None) -> None:
        """Accept the current layer (`X-Up-Dismiss-Layer`).

        An optional value can be provided to be passed back to the client."""
        # assert self.is_overlay -- the client simply ignores this on the root layer
        self.unpoly.options.dismiss_layer = value

    def open(self, **options: object) -> None:
        """Open a new layer (`X-Up-Open-Layer`) with the passed options."""
        self.unpoly.options.open_layer = options


class Cache:
    def __init__(self, unpoly: Unpoly):
        self.unpoly = unpoly
        major, minor, *_ = self.unpoly.version_info
        self._is_old = (major, minor) < (3, 11)

    def expire(self, pattern: str = "*") -> None:
        """
        Tell the client to remove all caches matching the pattern (`X-Up-Expire-Cache`).
        """
        if not self._is_old and pattern == "false":
            msg = "up.cache.expire(false) is no longer supported in Unpoly 3.11."
            warnings.warn(msg, DeprecationWarning, stacklevel=1)
            return

        self.unpoly.options.expire_cache = pattern

    def evict(self, pattern: str = "*") -> None:
        """
        Tell the client to evict all caches matching the pattern (`X-Up-Evict-Cache`).
        """
        self.unpoly.options.evict_cache = pattern

    def keep(self) -> None:
        """Tell the client to keep the cache."""
        if self._is_old:
            return self.expire("false")  # this is intentional

        msg = "up.cache.keep is no longer supported in Unpoly 3.11."
        warnings.warn(msg, DeprecationWarning, stacklevel=1)


class Unpoly:
    """The main entrypoint for communication with Unpoly"""

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
        """Returns true if the request is triggered via Unpoly.

        This basically checks if the `X-Up-Version` header is set."""
        return bool(self.options.version)

    def set_title(self, value: str) -> None:
        """Sets the title so Unpoly can update the <title> tag (`X-Up-Title`)."""
        self.options.title = value

    def emit(self, type: str, options: dict[str, object]) -> None:
        """Emit events to the frontend (`X-Up-Events`)."""
        self.options.events.append(dict(type=type, **options))

    @cached_property
    def cache(self) -> Cache:
        """Access to the :class:`.Cache` functionality"""
        return Cache(self)

    @property
    def version(self) -> str:
        """Unpoly version (`X-Up-Version`)."""
        return self.options.version

    @property
    def version_info(self) -> list[int | str]:
        """Unpoly version (`X-Up-Version`) parsed into a tuple."""
        parts = self.options.version.replace("-", ".").split(".")
        return [int(part) if part.isdigit() else part for part in parts]

    @property
    def target(self) -> str:
        """Gives access to the request's target (`X-Up-Target`).
        If the server set a new target it will return that instead."""
        return self.options.server_target or self.options.target

    @target.setter
    def target(self, new_target: str) -> None:
        self.options.server_target = new_target

    @property
    def mode(self) -> str:
        """Returns the request's mode (`X-Up-Mode`)."""
        return self.options.mode

    @property
    def origin_mode(self) -> str:
        """Returns the request's origin mode (`X-Up-Origin-Mode`)."""
        return self.options.origin_mode

    @cached_property
    def origin_layer(self) -> Layer:
        """Returns a :class:`.Layer` representing the origin mode
        The layer's main purpose is to expose the `is_root` and `is_overlay` properties.
        """
        return Layer(self, self.origin_mode, {})

    @property
    def context(self) -> dict[str, object]:
        """Returns the current context.
        Initially this is `X-Up-Context` but the server can modify the
        returned dictionary to update the values on the client."""
        return self.options.context

    @cached_property
    def layer(self) -> Layer:
        """Access the current :class:`.Layer` configuration."""
        return Layer(self, self.mode or "root", self.context)

    @property
    def validate(self) -> list[str]:
        """Returns the fields Unpoly is trying to validate (`X-Up-Validate`)."""
        return self.options.validate.split()

    @property
    def fail_target(self) -> str:
        """Gives access to the request's failure target (`X-Up-Fail-Target`).
        If the server set a new target it will return that instead."""
        return self.options.server_target or self.options.fail_target

    @property
    def fail_mode(self) -> str:
        """Returns the request's failure mode (`X-Up-Fail-Mode`)."""
        return self.options.fail_mode

    @property
    def fail_context(self) -> dict[str, object]:
        """Returns the current failure context (`X-Up-Fail-Context`)."""
        return self.options.fail_context

    @cached_property
    def fail_layer(self) -> Layer:
        """Access the current :class:`.Layer` configuration for failures."""
        return Layer(self, self.fail_mode or "root", self.fail_context)

    @property
    def needs_cookie(self) -> bool:
        """Checks whether the response should set the `_up_method` cookie."""
        return self.adapter.method != "GET" and not bool(self)

    def finalize_response(self, response: object) -> None:
        """Finalize the response by settings required headers & cookies.

        It should be noted that the response is passed as is to current adapter, which
        knows how to set headers on the response etc.
        """
        self.adapter.set_cookie(response, self.needs_cookie)

        if not self:
            return

        redirect_uri = self.adapter.redirect_uri(response)
        serialized_options = self.options.serialize(self.adapter)
        # Handle redirects
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
            if "?" in loc and "_up_" in loc:  # Not 100% exact, but will do
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
