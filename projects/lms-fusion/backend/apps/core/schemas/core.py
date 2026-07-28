"""
Core API schemas — reusable pagination, health, error shapes (Pydantic).

Used as building blocks by domain schemas (courses, research, auth, contact).
All schemas use Pydantic BaseModel per django-bolt conventions.
"""

from __future__ import annotations

from typing import Generic, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════════════════
# Health
# ═══════════════════════════════════════════════════════════════════════


class HealthResponse(BaseModel):
    """GET /apis/health"""

    status: str = "ok"
    service: str = "fusion-cms-bolt"
    version: str = "1.0.0"
    layer: str = "bolt-exclusive"


# ═══════════════════════════════════════════════════════════════════════
# Error
# ═══════════════════════════════════════════════════════════════════════


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    error: str
    code: int = 400


# ═══════════════════════════════════════════════════════════════════════
# Pagination
# ═══════════════════════════════════════════════════════════════════════


class PaginationMeta(BaseModel):
    """Pagination metadata returned with all list endpoints."""

    page: int
    per_page: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated API response envelope.

    Usage:
        courses = PaginatedResponse[CourseResponse](
            data=[...], pagination=PaginationMeta(page=1, total_pages=5)
        )
        return courses.model_dump()
    """

    data: list[T]
    pagination: PaginationMeta


# ═══════════════════════════════════════════════════════════════════════
# Single-item response
# ═══════════════════════════════════════════════════════════════════════


class SingleResponse(BaseModel, Generic[T]):
    """Single-item response envelope for detail endpoints."""

    data: T
