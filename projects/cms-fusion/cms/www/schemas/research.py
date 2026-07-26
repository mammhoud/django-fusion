"""
Research API schemas — Publications, Team (Pydantic).

Endpoints:
    GET  /apis/research/publications     → PaginatedResponse[PublicationResponse]
    GET  /apis/research/publications/<id> → SingleResponse[PublicationResponse]
    GET  /apis/research/team             → list[TeamMemberResponse]
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class PublicationResponse(BaseModel):
    """Single publication item in list or detail view."""

    id: int
    title: str
    slug: str = ""
    abstract: str = ""
    authors: str = ""
    category: str = ""
    published_at: Optional[str] = None
    featured_image: Optional[str] = None
    external_url: str = ""


class TeamMemberResponse(BaseModel):
    """Single team member item."""

    id: int
    name: str
    title: str = ""
    bio: str = ""
    email: str = ""
    photo: Optional[str] = None
    social_links: dict = {}
