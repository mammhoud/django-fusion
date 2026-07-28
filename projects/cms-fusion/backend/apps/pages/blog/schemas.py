"""
Blog, Events, Testimonials API schemas (Pydantic).

Endpoints:
    GET  /apis/blog              → PaginatedResponse[BlogPostResponse]
    GET  /apis/events            → list[EventResponse]
    GET  /apis/testimonials      → list[TestimonialResponse]
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class BlogPostResponse(BaseModel):
    """Single blog post in list or detail view."""

    id: int
    title: str
    slug: str = ""
    excerpt: str = ""
    content: str = ""
    author: str = ""
    category: str = ""
    image_url: Optional[str] = None
    published_at: Optional[str] = None
    is_published: bool = True


class EventResponse(BaseModel):
    """Single event item."""

    id: int
    title: str
    slug: str = ""
    description: str = ""
    location: str = ""
    event_date: Optional[str] = None
    image_url: Optional[str] = None
    is_published: bool = True


class TestimonialResponse(BaseModel):
    """Single testimonial item."""

    id: int
    name: str
    designation: str = ""
    quote: str = ""
    avatar_url: Optional[str] = None
    rating: float = 0.0
    is_active: bool = True
