"""
Enhanced renderers and response helpers for django-fusion.

Provides a standardized JSON response shape and a reusable ``JSONRenderer``
for both API views and fragment-pointer endpoints. The response format
matches the common pattern used by Django Ninja and other modern Django
API toolkits::

    {
      "status": 200,
      "message": "Success",
      "data": { ... }
    }

The module also exposes Pydantic-friendly schema helpers so fragment
responses can be documented through OpenAPI / Ninja automatically.
"""

from __future__ import annotations

import inspect
import json
from typing import Any, Mapping, Type
from urllib.parse import urljoin

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest, JsonResponse
from django.urls import NoReverseMatch, reverse


def _make_response_codes() -> dict[str, frozenset[int]]:
    """Build the canonical status-code groupings."""
    return {
        "information": frozenset(range(100, 102)),
        "success": frozenset(range(200, 207)),
        "redirect": frozenset(range(300, 309)),
        "client_error": frozenset(range(400, 413)) | frozenset({416, 418, 425, 429, 451}),
        "server_error": frozenset(range(500, 505)),
    }


RESPONSE_CODE_GROUPS = _make_response_codes()


def _status_to_message(status: int) -> str:
    """Return a human-readable message for a given HTTP status code."""
    if status in RESPONSE_CODE_GROUPS["success"]:
        return "Success"
    if status in RESPONSE_CODE_GROUPS["client_error"]:
        return "Client Error"
    if status in RESPONSE_CODE_GROUPS["server_error"]:
        return "Server Error"
    if status in RESPONSE_CODE_GROUPS["redirect"]:
        return "Redirect"
    if status in RESPONSE_CODE_GROUPS["information"]:
        return "Informational"
    return "Unknown Status"


class FusionJSONEncoder(DjangoJSONEncoder):
    """JSON encoder that extends Django's encoder with fusion-aware types.

    Currently defers to Django's built-in handling of ``Decimal``,
    ``datetime``, ``UUID``, etc. Subclass or replace ``default()`` to add
    serialization for custom fusion types (e.g. ``DataToken``, component
    pointers, lazy proxies).
    """

    def default(self, obj: Any) -> Any:
        # Defer to Django's encoder for Decimal, datetime, UUID, etc.
        return super().default(obj)


class FusionJSONRenderer:
    """Standardized JSON renderer for django-fusion API/fragment responses.

    Mirrors the shape of popular Django API toolkits while remaining
    framework-agnostic enough to use inside data adapters, bolt views, or
    plain Django views.

    Usage::

        renderer = FusionJSONRenderer()
        return renderer.render(request, {"fragment_url": "..."})
    """

    media_type: str = "application/json"
    encoder_class: Type[json.JSONEncoder] = FusionJSONEncoder

    def __init__(
        self,
        *,
        encoder_class: Type[json.JSONEncoder] | None = None,
        json_dumps_params: Mapping[str, Any] | None = None,
    ) -> None:
        if encoder_class is not None:
            self.encoder_class = encoder_class
        self.json_dumps_params: Mapping[str, Any] = dict(json_dumps_params or {})

    def render(
        self,
        request: HttpRequest,
        data: Any,
        *,
        response_status: int = 200,
        message: str | None = None,
    ) -> JsonResponse:
        """Render *data* as a standardized JSON response."""
        response_data = {
            "status": response_status,
            "message": message or _status_to_message(response_status),
            "data": data,
        }
        return JsonResponse(
            response_data,
            status=response_status,
            encoder=self.encoder_class,
            json_dumps_params=dict(self.json_dumps_params),
        )


def fusion_json_response(
    data: Any,
    *,
    status: int = 200,
    message: str | None = None,
    encoder_class: Type[json.JSONEncoder] = FusionJSONEncoder,
    json_dumps_params: Mapping[str, Any] | None = None,
) -> JsonResponse:
    """Convenience function that returns the standard response shape.

    Example::

        return fusion_json_response({
            "component": "pages.home",
            "fragment_url": "...",
        })
    """
    response_data = {
        "status": status,
        "message": message or _status_to_message(status),
        "data": data,
    }
    return JsonResponse(
        response_data,
        status=status,
        encoder=encoder_class,
        json_dumps_params=dict(json_dumps_params or {}),
    )


# ---------------------------------------------------------------------------
# Fragment-pointer payload builder
# ---------------------------------------------------------------------------


def fusion_response(
    component: Any,
    request: HttpRequest | None = None,
    *,
    fusion_render_first: bool | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the canonical fragment-pointer payload for a django-fusion component.

    ``component`` may be:

    * a ``RoutableComponent``/``FragmentComponent`` **class**,
    * an instance of such a component, or
    * a string fragment name (e.g. ``"pages.home"``).

    ``request`` is optional. When provided, the returned ``fragment_url`` will be
    an absolute URL if the request object supports ``build_absolute_uri`` or
    exposes the Host header.

    ``fusion_render_first`` can be used to override the component's own flag.
    ``extra`` is merged into the returned payload.

    The payload shape matches ``FusionFragmentPointer`` (component,
    ``fusion_render_first``, ``fragment_name``, ``fragment_url``) so fragment
    responses can be documented through OpenAPI/Ninja automatically.
    """
    # Resolve the component name and fragment identifier.
    if isinstance(component, str):
        component_name = component
        resolved_fragment_name = component
        resolved_render_first = fusion_render_first if fusion_render_first is not None else False
    else:
        is_class = inspect.isclass(component)
        component_name = component.__name__ if is_class else type(component).__name__

        instance: Any | None = None
        if is_class:
            try:
                instance = component()
            except Exception:
                instance = None
        else:
            instance = component

        target = instance if instance is not None else component

        if fusion_render_first is not None:
            resolved_render_first = fusion_render_first
        elif hasattr(target, "get_fusion_render_first"):
            resolved_render_first = target.get_fusion_render_first()
        else:
            resolved_render_first = bool(
                getattr(target, "fusion_render_first", False)
            )

        resolved_fragment_name = getattr(target, "fragment_name", None)
        if instance is not None:
            get_fragment_name = getattr(instance, "get_fragment_name", None)
            if callable(get_fragment_name):
                try:
                    resolved_fragment_name = get_fragment_name()
                except Exception:
                    pass

    if not resolved_fragment_name:
        raise ValueError(
            f"Cannot resolve fragment_name for component {component!r}"
        )

    from django_fusion.fragments.renderer import validate_fragment_name

    try:
        validate_fragment_name(resolved_fragment_name)
    except Exception as exc:
        raise ValueError(
            f"Invalid fragment_name {resolved_fragment_name!r} for component {component!r}: {exc}"
        ) from exc

    payload: dict[str, Any] = {}
    if extra:
        payload.update(extra)

    payload.update(
        {
            "component": component_name,
            "fusion_render_first": resolved_render_first,
            "fragment_name": resolved_fragment_name,
            "fragment_url": _build_fragment_url(resolved_fragment_name, request),
        }
    )

    return payload


def _build_fragment_url(fragment_name: str, request: HttpRequest | None = None) -> str:
    """Build a fragment URL for *fragment_name*."""
    try:
        path = reverse("fragments:render", kwargs={"fragment_name": fragment_name})
    except NoReverseMatch:
        path = f"/fragments/{fragment_name}/"

    if request is None:
        return path

    build_abs = getattr(request, "build_absolute_uri", None)
    if callable(build_abs):
        try:
            return build_abs(path)
        except Exception:
            pass

    request_url = getattr(request, "url", None)
    if request_url:
        try:
            return urljoin(request_url, path)
        except Exception:
            pass

    headers = getattr(request, "headers", None) or getattr(request, "META", None)
    host = None
    if headers:
        host = headers.get("host") or headers.get("HTTP_HOST")
    if host:
        scheme = getattr(request, "scheme", None) or "http"
        return f"{scheme}://{host}{path}"

    return path


# ---------------------------------------------------------------------------
# Schema generation helpers (Ninja/Pydantic-compatible)
# ---------------------------------------------------------------------------

try:
    from pydantic import BaseModel, Field

    class FusionFragmentSchema(BaseModel):
        """Schema for fragment-pointer responses.

        Used by OpenAPI/Ninja to document the canonical fragment payload.
        """

        status: int = Field(default=200, description="HTTP status code")
        message: str = Field(default="Success", description="Human-readable status")
        data: dict[str, Any] = Field(
            default_factory=dict,
            description=(
                "Fragment pointer payload (component, fragment_name, "
                "fragment_url, etc.)"
            ),
        )

    class FusionFragmentPointer(BaseModel):
        """Inner data shape of a fragment pointer response."""

        component: str = Field(..., description="Human-readable component identifier")
        fragment_name: str = Field(..., description="Registered django-fusion fragment name")
        fragment_url: str = Field(..., description="URL that returns the rendered HTML fragment")
        fusion_render_first: bool = Field(
            default=False,
            description="When True, render the server fragment first",
        )

except ImportError:  # pragma: no cover - Pydantic is optional
    BaseModel = None  # type: ignore[assignment]

    class _FallbackSchema:  # type: ignore[no-redef]
        """Fallback when Pydantic is not installed."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("Pydantic is required for FusionFragmentSchema")

    FusionFragmentSchema = _FallbackSchema  # type: ignore[misc]
    FusionFragmentPointer = _FallbackSchema  # type: ignore[misc]


__all__ = [
    "RESPONSE_CODE_GROUPS",
    "FusionJSONEncoder",
    "FusionJSONRenderer",
    "fusion_json_response",
    "fusion_response",
    "FusionFragmentSchema",
    "FusionFragmentPointer",
]
