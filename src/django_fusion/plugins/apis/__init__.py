"""
Optional API plugins for django-fusion.

The auth and django-bolt bridge are dependency-light at import time. Model
schema generation remains available when the project's schema dependency is
installed, but importing token helpers must not require it.
"""

from __future__ import annotations

from typing import Any

try:
    from django_fusion.plugins.apis.schemas import (
        SchemaRegistry,
        generate_schema,
        generate_schemas_for_app,
        get_schema,
    )
except ModuleNotFoundError as exc:  # optional ninja-schema dependency
    _schema_import_error = exc

    def _missing_schema_dependency(*args: Any, **kwargs: Any) -> Any:
        raise ModuleNotFoundError(
            "Model schema generation requires the django-fusion API schema "
            "dependencies (install the project's API extras)."
        ) from _schema_import_error

    SchemaRegistry = None  # type: ignore[assignment,misc]
    generate_schema = _missing_schema_dependency
    generate_schemas_for_app = _missing_schema_dependency
    get_schema = _missing_schema_dependency

from django_fusion.plugins.apis.auth import (
    BoltTokenConfig,
    FusionTokenError,
    TokenUserError,
    build_bolt_auth,
    extract_bearer_token,
    get_token_config,
    refresh_payload,
    token_payload,
    user_token_payload,
    verify_request_user,
    verify_token_user,
)
from django_fusion.plugins.apis.views import APIApplication, APISViewMixin
from django_fusion.plugins.apis.openapi import OpenAPISpec, openapi_docs, openapi_json
from django_fusion.plugins.apis.viewsets import (
    FusionApiViewset,
    api_viewset_registry,
    get_api_viewset,
    mount_api_viewsets,
    register_api_viewset,
)

from . import bolt  # noqa: F401 - expose the bolt bridge submodule
from .bolt import (
    BoltAPIApplication,
    BoltNotInstalledError,
    build_bolt_api,
    generate_msgspec_schema,
    is_bolt_installed,
    mount_application,
    mount_model_crud,
    mount_refresh_endpoint,
    mount_token_endpoint,
)

__all__ = [
    "SchemaRegistry",
    "generate_schema",
    "generate_schemas_for_app",
    "get_schema",
    "APIApplication",
    "APISViewMixin",
    "FusionApiViewset",
    "api_viewset_registry",
    "get_api_viewset",
    "mount_api_viewsets",
    "register_api_viewset",
    "BoltTokenConfig",
    "FusionTokenError",
    "TokenUserError",
    "build_bolt_auth",
    "extract_bearer_token",
    "get_token_config",
    "refresh_payload",
    "token_payload",
    "user_token_payload",
    "verify_request_user",
    "verify_token_user",
    "BoltAPIApplication",
    "BoltNotInstalledError",
    "build_bolt_api",
    "generate_msgspec_schema",
    "is_bolt_installed",
    "mount_application",
    "mount_model_crud",
    "mount_refresh_endpoint",
    "mount_token_endpoint",
    "bolt",
    "OpenAPISpec",
    "openapi_json",
    "openapi_docs",
]
