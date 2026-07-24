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

import json
from typing import Any, Mapping, Type

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest, JsonResponse


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
    "FusionFragmentSchema",
    "FusionFragmentPointer",
]
