"""Pydantic response schemas.

This module hosts the generic ``APIResponse`` envelope used across the
framework and exposed historically through
``django_fusion.site.schemas.response``.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    """Generic API response envelope.

    Attributes:
        status: Either ``"success"`` or ``"error"``.
        data: Payload returned by the endpoint.
        message: Optional human-readable message.
    """

    status: str = "success"
    data: Any = None
    message: str = ""

    class Config:
        arbitrary_types_allowed = True


__all__ = ["APIResponse"]
