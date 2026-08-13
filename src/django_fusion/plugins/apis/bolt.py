"""
django-bolt bridge for the django-fusion ``apis`` plugin.

Restores the django-bolt integration *inside* django-fusion so a single
``Application`` (with its viewsets) can be served two ways at once:

* **Bolt routes** — high-performance Rust-backed API endpoints registered on
  a ``django_bolt.BoltAPI`` instance.
* **Dual-mode responses** — every bolt route resolves the effective
  render-first mode (header → ``render_first_mapping`` → ``fusion_render_first``
  → settings) and answers with **either** a component fragment HTML with data
  (render-first) **or** a codec-encoded JSON API payload (data mode), exactly
  like :meth:`django_fusion.plugins.apis.views.APISViewMixin.respond`.

Auto API generation
-------------------
``generate_msgspec_schema`` builds a ``msgspec.Struct`` from a Django model's
concrete fields via :func:`msgspec.defstruct`, so bolt endpoints get typed
request/response bodies without hand-writing one struct per resource.

Availability check
------------------
``is_bolt_installed()`` returns whether ``django_bolt`` is importable. When it
is *not* installed every factory degrades gracefully:

* ``build_bolt_api()`` returns ``None``,
* ``mount_application()`` / ``mount_model_crud()`` become no-ops,
* ``BoltAPIApplication.mount_on_bolt()`` logs a hint and returns ``None``.

This mirrors how the formint sidecar keeps ``django_bolt`` optional in
``INSTALLED_APPS``.
"""

from __future__ import annotations

import importlib.util
import inspect
import logging
from typing import Any

from django.db.models import Model

from django_fusion.plugins.apis.auth import (
    BoltTokenConfig,
    TokenUserError,
    build_bolt_auth,
    refresh_payload,
    token_payload,
    user_token_payload,
)
from django_fusion.plugins.apis.views import APISViewMixin
from django_fusion.routes.core.sites import Application

logger = logging.getLogger(__name__)

__all__ = [
    "BoltAPIApplication",
    "BoltNotInstalledError",
    "build_bolt_api",
    "generate_msgspec_schema",
    "is_bolt_installed",
    "mount_application",
    "mount_model_crud",
    "BoltTokenConfig",
    "build_bolt_auth",
    "mount_token_endpoint",
    "mount_refresh_endpoint",
    "user_token_payload",
]


def is_bolt_installed() -> bool:
    """Return whether a usable ``django_bolt`` package is importable.

    The monorepo may contain the documentation-only django-bolt placeholder,
    which has a package name but no ``BoltAPI``. Checking the public symbols
    prevents that placeholder from being mistaken for an installed runtime.
    """
    if importlib.util.find_spec("django_bolt") is None:
        return False
    try:
        from django_bolt import BoltAPI  # type: ignore[import-not-found]
        from django_bolt.openapi import OpenAPIConfig  # type: ignore[import-not-found]
    except (ImportError, ModuleNotFoundError, AttributeError):
        return False
    return callable(BoltAPI) and callable(OpenAPIConfig)


class BoltNotInstalledError(RuntimeError):
    """Raised when a bolt operation is requested but ``django_bolt`` is absent."""


def _require_bolt():
    """Import and return the ``django_bolt`` module or raise."""
    if not is_bolt_installed():
        raise BoltNotInstalledError(
            "django-bolt is not installed. Add 'django-bolt' to your "
            "requirements (or install it) to use bolt API generation."
        )
    import django_bolt  # type: ignore[import-not-found]

    return django_bolt


def generate_msgspec_schema(
    model: type[Model],
    *,
    name: str | None = None,
    fields: list[str] | None = None,
) -> Any:
    """Generate a ``msgspec.Struct`` schema class for *model*.

    Field types default to ``object`` so any ORM value serialises; override
    by passing explicit ``(name, type, default)`` entries via *fields*.
    A ``from_model`` classmethod is attached so bolt endpoints can convert
    ORM instances to the struct in one call.

    Arguments:
        model: The Django model class to introspect.
        name: Optional struct name (default ``f"{model.__name__}Schema"``).
        fields: Optional ``[(name, type, default)]`` triples. When omitted,
            one ``(attname, object)`` pair is generated per concrete field.
    """
    import msgspec  # type: ignore[import-not-found]

    schema_name = name or f"{model.__name__}Schema"

    if fields is None:
        field_specs: list[tuple[str, Any, Any]] = []
        for field in model._meta.concrete_fields:  # type: ignore[attr-defined]
            field_specs.append((field.attname, object, msgspec.UNSET))
    else:
        field_specs = [(f, object, msgspec.UNSET) for f in fields]

    def _from_model(cls, obj: Any) -> Any:
        return cls(**{spec[0]: getattr(obj, spec[0]) for spec in field_specs})

    return msgspec.defstruct(
        schema_name,
        field_specs,
        namespace={"from_model": classmethod(_from_model)},
        dict=True,
        kw_only=True,
    )


def build_bolt_api(
    *,
    prefix: str = "/bolt",
    title: str = "Fusion API",
    version: str = "1.0.0",
    openapi_path: str = "/bolt/docs",
    auth: list[Any] | None = None,
    token_config: BoltTokenConfig | None = None,
) -> Any | None:
    """Build a configured ``BoltAPI`` instance, or ``None`` if bolt is absent.

    Returns ``None`` (never raises) when ``django_bolt`` is not installed so
    callers can mount conditionally::

        api = build_bolt_api(prefix="/bolt", title="POS API")
        if api is not None:
            mount_model_crud(api, Product)
    """
    if not is_bolt_installed():
        return None
    bolt = _require_bolt()
    openapi_config = bolt.OpenAPIConfig(
        title=title,
        version=version,
        path=openapi_path,
    )
    kwargs = {
        "prefix": prefix,
        "openapi_config": openapi_config,
    }
    # ``namespace`` was added after the first public Bolt release. Prefer it
    # when available, but do not make the fusion plugin version-sensitive.
    try:
        api = bolt.BoltAPI(
            **kwargs,
            namespace=title.lower().replace(" ", "-"),
        )
    except TypeError:
        api = bolt.BoltAPI(**kwargs)
    # Keep the resolved backends on the instance so projects can reuse the
    # same auth policy for manually declared routes and generated CRUD.
    api.fusion_auth = auth if auth is not None else build_bolt_auth(token_config)
    api.fusion_token_config = token_config or BoltTokenConfig.from_django_settings()
    return api


def _viewset_name(viewset: Any) -> str:
    """Return a URL-safe name for a viewset instance/class."""
    name = getattr(viewset, "name", None) or getattr(viewset, "__name__", None) or "resource"
    return str(name).replace("_", "-").lower()


class BoltAPIApplication(APISViewMixin, Application):
    """An ``Application``-style class that can mount itself on a BoltAPI.

    Subclass it like ``APIApplication`` but gain ``mount_on_bolt()``::

        class ProductsAPI(BoltAPIApplication):
            title = "Products"
            fusion_render_first = True
            template_name = "components/products/list.html"
            viewsets = [ProductsViewset]

        api = build_bolt_api(prefix="/api")
        if api is not None:
            ProductsAPI().mount_on_bolt(api)

    Each declared viewset is registered as ``GET/POST/PATCH/DELETE`` routes
    under ``{prefix}/{viewset_name}`` (and ``/{pk}`` for retrieve/update/
    delete). Every handler answers through the dual-mode :meth:`respond`
    contract, so a single route can serve a component fragment HTML with data
    or a codec JSON API payload depending on the effective render-first mode.
    """

    #: Viewsets to mount (same attribute used by django-fusion ``Application``).
    viewsets: list[Any] = []

    #: Optional auth backends passed to every registered bolt route.
    auth: list[Any] | None = None

    #: Optional guards passed to every registered bolt route.
    guards: list[Any] | None = None

    # ------------------------------------------------------------------
    # Bolt mounting
    # ------------------------------------------------------------------

    def mount_on_bolt(self, api: Any, *, prefix: str | None = None) -> Any | None:
        """Mount this application's viewsets on *api* as dual-mode bolt routes.

        Returns the bolt api (for chaining) or ``None`` when bolt is absent.
        """
        if api is None or not is_bolt_installed():
            logger.info(
                "apis.bolt: django-bolt not installed — %s not mounted",
                self.__class__.__name__,
            )
            return None

        mount_application(api, self, prefix=prefix, auth=self.auth, guards=self.guards)
        return api

    def _bolt_respond(self, request: Any, data: Any, *, view_name: str | None = None) -> Any:
        """Dual-mode respond for bolt requests.

        Bolt's ``Request`` is not a Django ``HttpRequest``; wrap it in a tiny
        adapter exposing ``headers`` so :meth:`get_effective_render_first`
        can honour the ``X-Fusion-Render-First`` header, then delegate to the
        shared :meth:`respond` contract.
        """
        return self.respond(_BoltRequestAdapter(request), data, view_name=view_name)


class _BoltRequestAdapter:
    """Minimal request adapter exposing a ``headers`` mapping to the apis mixin."""

    __slots__ = ("_request",)

    def __init__(self, request: Any) -> None:
        self._request = request

    @property
    def headers(self) -> dict[str, str]:
        raw = getattr(self._request, "headers", {}) or {}
        try:
            values = {str(k): str(v) for k, v in raw.items()}
        except Exception:  # pragma: no cover - defensive
            return {}
        # Django-style callers use canonical names while Bolt clients may
        # expose lower-case ASGI names; provide both without retaining secrets.
        values.update({key.lower(): value for key, value in values.items()})
        return values


def mount_application(
    api: Any,
    application: BoltAPIApplication,
    *,
    prefix: str | None = None,
    auth: list[Any] | None = None,
    guards: list[Any] | None = None,
) -> None:
    """Mount *application*'s viewsets on a BoltAPI *api*.

    For each viewset in ``application.viewsets`` register:

    ==========  =========================================================
    Method      Route
    ==========  =========================================================
    GET         ``{prefix}/{name}``      → viewset.list (or get)
    GET         ``{prefix}/{name}/{pk}`` → viewset.get
    POST        ``{prefix}/{name}``      → viewset.create (or post)
    PATCH       ``{prefix}/{name}/{pk}`` → viewset.update
    DELETE      ``{prefix}/{name}/{pk}`` → viewset.delete
    ==========  =========================================================

    Handlers call the viewset action to obtain data, then answer through the
    application's dual-mode :meth:`BoltAPIApplication.respond` contract.
    """
    if api is None or not is_bolt_installed():
        return

    route_auth = auth if auth is not None else getattr(api, "fusion_auth", None)
    base = (prefix or f"/{_viewset_name(application)}").rstrip("/")

    for viewset in list(getattr(application, "viewsets", []) or []):
        name = _viewset_name(viewset)
        path = f"{base}/{name}"
        application._bolt_respond  # noqa: B018 - ensure attribute exists (doc)

        @api.get(path, auth=route_auth, guards=guards)
        async def _list(request: Any, _vs: Any = viewset, _app: Any = application, _n: str = name) -> Any:
            action = getattr(_vs, "list", None) or getattr(_vs, "get", None)
            data = await _call_action(action, _vs, request, pk=None)
            return _app._bolt_respond(request, data, view_name=f"{_n}/list")

        @api.get(f"{path}/{{pk}}", auth=route_auth, guards=guards)
        async def _retrieve(request: Any, pk: Any, _vs: Any = viewset, _app: Any = application, _n: str = name) -> Any:
            action = getattr(_vs, "get", None)
            data = await _call_action(action, _vs, request, pk=pk)
            return _app._bolt_respond(request, data, view_name=f"{_n}/get")

        @api.post(path, auth=route_auth, guards=guards)
        async def _create(request: Any, _vs: Any = viewset, _app: Any = application, _n: str = name) -> Any:
            action = getattr(_vs, "create", None) or getattr(_vs, "post", None)
            data = await _call_action(action, _vs, request, pk=None)
            return _app._bolt_respond(request, data, view_name=f"{_n}/create")

        @api.patch(f"{path}/{{pk}}", auth=route_auth, guards=guards)
        async def _update(request: Any, pk: Any, _vs: Any = viewset, _app: Any = application, _n: str = name) -> Any:
            action = getattr(_vs, "update", None)
            data = await _call_action(action, _vs, request, pk=pk)
            return _app._bolt_respond(request, data, view_name=f"{_n}/update")

        @api.delete(f"{path}/{{pk}}", auth=route_auth, guards=guards, status_code=204)
        async def _delete(request: Any, pk: Any, _vs: Any = viewset, _app: Any = application, _n: str = name) -> Any:
            action = getattr(_vs, "delete", None)
            data = await _call_action(action, _vs, request, pk=pk)
            return _app._bolt_respond(request, data, view_name=f"{_n}/delete")

        logger.info("apis.bolt: mounted %s at %s", name, path)


def mount_token_endpoint(
    api: Any,
    *,
    path: str = "/auth/token",
    config: BoltTokenConfig | None = None,
    user_required: bool = False,
) -> Any | None:
    """Register a public JWT issuance endpoint on a BoltAPI.

    The endpoint deliberately accepts only an opaque subject/device id and a
    role. Provider credentials and signing secrets stay server-side. The
    returned handler is useful for tests or projects that want to inspect the
    registration; ``None`` means Bolt is unavailable.
    """
    if api is None or not is_bolt_installed():
        return None

    try:
        import msgspec
        from django_bolt.auth import AllowAny, IsAuthenticated
    except (ImportError, ModuleNotFoundError) as exc:  # pragma: no cover - runtime dependency
        raise BoltNotInstalledError(
            "django-bolt token routes require msgspec and django_bolt.auth"
        ) from exc

    class TokenRequest(msgspec.Struct, kw_only=True):
        subject: str | None = None
        device_id: str | None = None
        role: str = "viewer"
        ttl: int | None = None

    route_auth = build_bolt_auth(config) if user_required else []
    route_guards = [IsAuthenticated()] if user_required else [AllowAny()]

    @api.post(path, auth=route_auth, guards=route_guards)
    async def issue_token(request: Any, body: TokenRequest) -> dict[str, Any]:
        ttl = min(max(body.ttl or 3600, 60), 86_400)
        if user_required:
            user = getattr(request, "user", None) or getattr(request, "auth", None)
            if not getattr(user, "is_authenticated", False) or not getattr(user, "is_active", False):
                raise TokenUserError("An active authenticated user is required")
            requested_subject = (body.subject or "").strip()
            if requested_subject and requested_subject != str(user.pk):
                raise TokenUserError("A token can only be issued for the current user")
            return user_token_payload(user, ttl_seconds=ttl, config=config)
        subject = (body.subject or body.device_id or "").strip()
        if not subject:
            return {"detail": "subject is required"}
        return token_payload(subject, role=body.role, ttl_seconds=ttl, config=config)

    return issue_token


def mount_refresh_endpoint(
    api: Any,
    *,
    path: str = "/auth/refresh",
    config: BoltTokenConfig | None = None,
) -> Any | None:
    """Register refresh-token rotation on a BoltAPI.

    Refresh tokens are rotated with every successful request. Invalid or
    expired tokens return a structured error so clients can clear local auth
    state and use their configured compatibility road.
    """
    if api is None or not is_bolt_installed():
        return None

    try:
        import msgspec
        from django_bolt.auth import AllowAny
    except (ImportError, ModuleNotFoundError) as exc:  # pragma: no cover - runtime dependency
        raise BoltNotInstalledError(
            "django-bolt refresh routes require msgspec and django_bolt.auth"
        ) from exc

    class RefreshRequest(msgspec.Struct, kw_only=True):
        refresh_token: str

    @api.post(path, auth=[], guards=[AllowAny()])
    async def refresh_token(request: Any, body: RefreshRequest) -> dict[str, Any]:
        try:
            return refresh_payload(body.refresh_token, config=config)
        except Exception as exc:  # noqa: BLE001 - normalize token failures
            return {"detail": str(exc)}

    return refresh_token


async def _request_body(request: Any) -> dict[str, Any]:
    """Read a Bolt JSON body into a plain dict across Bolt versions."""
    body = getattr(request, "json", {})
    if callable(body):
        body = body()
    if inspect.isawaitable(body):
        body = await body
    if hasattr(body, "items"):
        return dict(body.items())
    try:
        import msgspec

        return dict(msgspec.structs.asdict(body))
    except (ImportError, TypeError, AttributeError):
        return {}


async def _call_action(action: Any, viewset: Any, request: Any, *, pk: Any) -> Any:
    """Invoke a viewset action tolerantly (sync or async, with/without pk)."""
    if action is None:
        return {"viewset": _viewset_name(viewset), "action": "unsupported"}

    kwargs: dict[str, Any] = {}
    if pk is not None:
        kwargs["pk"] = pk

    try:
        result = action(request, **kwargs) if kwargs else action(request)
    except TypeError:
        try:
            result = action(**kwargs) if kwargs else action()
        except TypeError:
            return {"viewset": _viewset_name(viewset), "action": "signature-mismatch"}

    if inspect.isawaitable(result):
        return await result
    return result


def mount_model_crud(
    api: Any,
    model: type[Model],
    *,
    prefix: str | None = None,
    schema: Any | None = None,
    auth: list[Any] | None = None,
    guards: list[Any] | None = None,
) -> Any | None:
    """Register full CRUD bolt routes for a single Django *model*.

    Uses ``generate_msgspec_schema(model)`` for typed bodies (or pass an
    explicit *schema*). Routes::

        GET    {prefix}          → list
        GET    {prefix}/{pk}     → retrieve
        POST   {prefix}          → create
        PATCH  {prefix}/{pk}     → update
        DELETE {prefix}/{pk}     → delete

    Returns the generated schema (or ``None`` when bolt is absent).
    """
    if api is None or not is_bolt_installed():
        return None

    route_auth = auth if auth is not None else getattr(api, "fusion_auth", None)
    struct = schema or generate_msgspec_schema(model)
    base = (prefix or f"/{model._meta.model_name}").rstrip("/")

    async def _rows(queryset: Any) -> list[Any]:
        rows = []
        async for obj in queryset:  # type: ignore[union-attr]
            rows.append(struct.from_model(obj))
        return rows

    @api.get(base, response_model=list[struct], auth=route_auth, guards=guards)
    async def _list(request: Any) -> Any:
        return await _rows(model.objects.all())

    @api.get(f"{base}/{{pk}}", response_model=struct, auth=route_auth, guards=guards)
    async def _retrieve(request: Any, pk: Any) -> Any:
        try:
            return struct.from_model(await model.objects.aget(pk=pk))
        except model.DoesNotExist:  # type: ignore[attr-defined]
            return {"error": "not found"}

    @api.post(base, response_model=struct, auth=route_auth, guards=guards)
    async def _create(request: Any) -> Any:
        body = await _request_body(request)
        return struct.from_model(await model.objects.acreate(**body))

    @api.patch(f"{base}/{{pk}}", response_model=struct, auth=route_auth, guards=guards)
    async def _update(request: Any, pk: Any) -> Any:
        body = await _request_body(request)
        obj = await model.objects.aget(pk=pk)
        for key, value in body.items():
            setattr(obj, key, value)
        await obj.asave()
        return struct.from_model(obj)

    @api.delete(f"{base}/{{pk}}", status_code=204, auth=route_auth, guards=guards)
    async def _delete(request: Any, pk: Any) -> None:
        obj = await model.objects.aget(pk=pk)
        await obj.adelete()

    logger.info("apis.bolt: mounted CRUD for %s at %s", model.__name__, base)
    return struct
