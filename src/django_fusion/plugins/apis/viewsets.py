"""Declarative model-API viewsets for the django-fusion ``apis`` plugin.

``FusionApiViewset`` is a single, dual-mode class that serves full JSON CRUD
for one Django model without a per-resource view. Products configure a
subclass (or a settings entry) with the model, field projection, and write
allowlist, and inherit tenant scoping, serialization, and the render-first /
data-mode response contract from the ``apis`` plugin.

Registry
--------
Viewsets can be registered in two equivalent ways:

1. Programmatically::

    from django_fusion.plugins.apis.viewsets import register_api_viewset
    register_api_viewset("products", ProductApiViewset)

2. Via settings (``FUSION_API_VIEWSETS``)::

    FUSION_API_VIEWSETS = {
        "products": {"viewset": "myapp.apis.ProductApiViewset"},
        "orders": {
            "model": "myapp.Order",
            "read_fields": ["id", "number", "total"],
            "write_fields": ["number", "total"],
            "required_fields": ["number"],
        },
    }

``mount_api_viewsets(prefix="api/")`` returns URL patterns for every registered
slug (``<prefix><slug>/`` and ``<prefix><slug>/<pk>/``). Settings entries are
resolved lazily so imports stay cheap.
"""
from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from typing import Any

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.urls import path
from django.utils.module_loading import import_string
from django.views import View

from django_fusion.plugins.apis.views import APISViewMixin

__all__ = [
    "FusionApiViewset",
    "register_api_viewset",
    "get_api_viewset",
    "mount_api_viewsets",
    "api_viewset_registry",
]


# ---------------------------------------------------------------------------
# Serialization helpers (mirror the proven ``apps.core.resources`` convention:
# Decimal → string, date/datetime → ISO-8601, everything else JSON-native).
# ---------------------------------------------------------------------------


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _model_has_field(model: type[models.Model], field_name: str) -> bool:
    return any(f.name == field_name for f in model._meta.concrete_fields)


# ---------------------------------------------------------------------------
# Viewset
# ---------------------------------------------------------------------------


class FusionApiViewset(View, APISViewMixin):
    """Generic, dual-mode JSON CRUD viewset for one model.

    Class attributes
    ----------------
    model:            Django model (required).
    read_fields:      projection returned in list/detail payloads.
    write_fields:     allowlist accepted on create/update.
    required_fields:  fields that must be present on create.
    lookup_field:     URL kwarg used for detail routes (default ``"pk"``).
    tenant_field:     model field used to scope reads/writes by tenant
                      (default ``"workspace_id"``). Set to ``None`` to disable.
    tenant_resolver:  optional ``callable(request) -> tenant_id`` override.
    fusion_render_first / template_name / schema_class:
                      inherited dual-mode contract (see ``APISViewMixin``).
    """

    model: type[models.Model] | None = None
    read_fields: tuple[str, ...] = ()
    write_fields: tuple[str, ...] = ()
    required_fields: tuple[str, ...] = ()
    lookup_field: str = "pk"
    tenant_field: str | None = "workspace_id"
    tenant_resolver: Callable[[HttpRequest], Any] | None = None

    # ------------------------------------------------------------------
    # Tenant scoping
    # ------------------------------------------------------------------

    def get_tenant_id(self, request: HttpRequest) -> Any:
        if self.tenant_resolver is not None:
            return self.tenant_resolver(request)
        if self.tenant_field:
            user = getattr(request, "user", None)
            profile = getattr(user, "profile", None)
            return getattr(profile, "workspace_id", None)
        return None

    def get_queryset(self, request: HttpRequest):
        assert self.model is not None, "FusionApiViewset.model must be set."
        queryset = self.model.objects.all()
        if self.tenant_field and _model_has_field(self.model, self.tenant_field):
            tenant_id = self.get_tenant_id(request)
            if tenant_id is not None:
                queryset = queryset.filter(**{self.tenant_field: tenant_id})
        return queryset

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def serialize(self, instance: models.Model) -> dict[str, Any]:
        values = self.model._default_manager.filter(pk=instance.pk).values(*self.read_fields).first()
        if values is None:
            return {}
        return {key: _json_value(value) for key, value in values.items()}

    def _resolve_relation(self, field_name: str, value: Any, instance: models.Model):
        field = self.model._meta.get_field(field_name)
        related_model = field.remote_field.model
        queryset = related_model.objects.filter(pk=value)
        tenant_id = self.get_tenant_id_from_instance(instance)
        if tenant_id is not None and _model_has_field(related_model, self.tenant_field or ""):
            queryset = queryset.filter(**{self.tenant_field: tenant_id})
        try:
            return queryset.get(), None
        except related_model.DoesNotExist:
            return None, f"{field_name} does not exist or is outside your workspace."

    def get_tenant_id_from_instance(self, instance: models.Model) -> Any:
        if self.tenant_field and _model_has_field(self.model, self.tenant_field):
            return getattr(instance, self.tenant_field, None)
        return None

    def _apply_payload(self, instance: models.Model, data: dict[str, Any]):
        errors: dict[str, str] = {}
        for field_name in self.write_fields:
            if field_name not in data:
                continue
            value = data[field_name]
            model_field = self.model._meta.get_field(field_name)
            if getattr(model_field, "is_relation", False):
                related, error = self._resolve_relation(field_name, value, instance)
                if error:
                    errors[field_name] = error
                    continue
                setattr(instance, field_name, related)
            else:
                try:
                    cleaned = model_field.clean(value, instance)
                except (ValidationError, TypeError, ValueError) as exc:
                    errors[field_name] = str(exc)
                    continue
                setattr(instance, field_name, cleaned)
        return errors

    # ------------------------------------------------------------------
    # HTTP handlers
    # ------------------------------------------------------------------

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        pk = kwargs.get(self.lookup_field)
        if pk is not None:
            instance = self.get_queryset(request).filter(pk=pk).first()
            if instance is None:
                return self._not_found()
            return self.respond(request, self.serialize(instance), view_name=f"{self.__class__.__name__}.detail")
        rows = [self.serialize(instance) for instance in self.get_queryset(request)[:100]]
        return self.respond(request, {"results": rows, "count": len(rows)}, view_name=f"{self.__class__.__name__}.list")

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        data = self._body_json(request)
        if data is None:
            return self._bad_request("Request body must be valid JSON.")
        missing = [name for name in self.required_fields if not data.get(name)]
        if missing:
            return self._bad_request(dict.fromkeys(missing, "This field is required."))
        instance = self.model()
        if self.tenant_field and _model_has_field(self.model, self.tenant_field):
            tenant_id = self.get_tenant_id(request)
            if tenant_id is None:
                return self._bad_request({self.tenant_field: "A tenant scope is required."})
            setattr(instance, self.tenant_field, tenant_id)
        errors = self._apply_payload(instance, data)
        if errors:
            return self._bad_request(errors)
        instance.save()
        return self.respond(request, self.serialize(instance), view_name=f"{self.__class__.__name__}.create", status=201)

    def patch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        instance = self.get_queryset(request).filter(pk=kwargs.get(self.lookup_field)).first()
        if instance is None:
            return self._not_found()
        data = self._body_json(request)
        if data is None:
            return self._bad_request("Request body must be valid JSON.")
        errors = self._apply_payload(instance, data)
        if errors:
            return self._bad_request(errors)
        instance.save()
        return self.respond(request, self.serialize(instance), view_name=f"{self.__class__.__name__}.update")

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        deleted, _ = self.get_queryset(request).filter(pk=kwargs.get(self.lookup_field)).delete()
        if not deleted:
            return self._not_found()
        return self.respond(request, {"deleted": True}, view_name=f"{self.__class__.__name__}.delete")

    # ------------------------------------------------------------------
    # Response helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _body_json(request: HttpRequest) -> dict[str, Any] | None:
        import json

        try:
            return json.loads(request.body or b"{}")
        except (TypeError, ValueError):
            return None

    def _not_found(self) -> HttpResponse:
        from django.http import JsonResponse

        return JsonResponse({"detail": "Not found."}, status=404)

    def _bad_request(self, detail: Any) -> HttpResponse:
        from django.http import JsonResponse

        if isinstance(detail, str):
            return JsonResponse({"detail": detail}, status=400)
        return JsonResponse(detail, status=400)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

#: slug → FusionApiViewset subclass (or a lazy factory).
api_viewset_registry: dict[str, type[FusionApiViewset]] = {}


def register_api_viewset(slug: str, viewset: type[FusionApiViewset]) -> type[FusionApiViewset]:
    """Register an API viewset class under *slug*."""
    api_viewset_registry[slug] = viewset
    return viewset


def get_api_viewset(slug: str) -> type[FusionApiViewset] | None:
    """Return the registered viewset for *slug* (resolving settings lazily)."""
    if slug in api_viewset_registry:
        return api_viewset_registry[slug]
    configs = getattr(settings, "FUSION_API_VIEWSETS", None) or {}
    config = configs.get(slug)
    if not config:
        return None
    viewset = _viewset_from_config(config)
    if viewset is not None:
        api_viewset_registry[slug] = viewset
    return viewset


def _viewset_from_config(config: dict[str, Any]) -> type[FusionApiViewset] | None:
    if "viewset" in config:
        return import_string(config["viewset"])
    if "model" in config:
        model = django_apps.get_model(config["model"])
        attrs = {
            "model": model,
            "read_fields": tuple(config.get("read_fields", [])),
            "write_fields": tuple(config.get("write_fields", [])),
            "required_fields": tuple(config.get("required_fields", [])),
        }
        return type(f"Auto{model.__name__}ApiViewset", (FusionApiViewset,), attrs)
    return None


def mount_api_viewsets(prefix: str = "api/") -> list:
    """Return URL patterns for every registered API viewset.

    Each slug mounts two patterns: the collection (``<prefix><slug>/``) and the
    detail (``<prefix><slug>/<pk>/``).
    """
    patterns: list = []
    for slug, viewset in api_viewset_registry.items():
        view = viewset.as_view()
        patterns.append(path(f"{prefix}{slug}/", view, name=f"fusion_api_{slug}_list"))
        patterns.append(path(f"{prefix}{slug}/<int:pk>/", view, name=f"fusion_api_{slug}_detail"))
    return patterns
