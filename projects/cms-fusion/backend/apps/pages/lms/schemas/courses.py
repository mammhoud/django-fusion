"""
Course API schemas — Course catalog, categories, detail (Pydantic).

Endpoints:
    GET  /apis/courses              → PaginatedResponse[CourseResponse]
    GET  /apis/courses/<id>          → SingleResponse[CourseResponse]
    GET  /apis/courses/categories    → list[CategoryResponse]
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class CourseResponse(BaseModel):
    """Single course item in list or detail view."""

    id: int
    title: str
    slug: str = ""
    description: str = ""
    short_description: str = ""
    category: str = ""
    skill_level: str = "beginner"
    language: str = "English"
    price: float = 0.0
    price_type: str = "Free"
    rating: float = 0.0
    instructor: str = ""
    thumbnail: Optional[str] = None
    duration: str = ""
    enrolled_count: int = 0
    created_at: Optional[str] = None


class CategoryResponse(BaseModel):
    """Course category item."""

    id: int
    name: str
    slug: str = ""
    course_count: int = 0
    icon: str = ""
    description: str = ""
