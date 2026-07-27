"""
LMS site data schemas — Features, Instructors, FAQ, Dashboard, Products (Pydantic).

Endpoints:
    GET  /apis/lms/features          → list[FeatureResponse]
    GET  /apis/lms/instructors       → list[InstructorResponse]
    GET  /apis/lms/faq               → list[FaqResponse]
    GET  /apis/lms/dashboard         → DashboardResponse
    GET  /apis/lms/products          → list[ProductResponse]
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class FeatureResponse(BaseModel):
    """A single feature card item."""

    id: int
    page: str = "home_1"
    title: str
    description: str
    icon_url: Optional[str] = None
    icon_class: str = ""
    sort_order: int = 0


class InstructorResponse(BaseModel):
    """A single instructor profile item."""

    id: int
    name: str
    designation: str = ""
    bio: str = ""
    avatar_url: Optional[str] = None
    rating: float = 0.0
    course_count: int = 0
    student_count: int = 0
    sort_order: int = 0
    social_links: dict = {}


class FaqItem(BaseModel):
    """A single FAQ item."""

    id: int
    page: str = "home_1"
    question: str
    answer: str
    sort_order: int = 0


class DashboardCounter(BaseModel):
    """A single dashboard counter stat."""

    id: int
    label: str
    value: int
    icon_class: str = ""
    prefix: str = ""
    suffix: str = ""


class DashboardResponse(BaseModel):
    """Full dashboard data response."""

    counters: list[DashboardCounter] = []
    enrolled_courses: list[dict] = []
    wishlist: list[dict] = []
    reviews: list[dict] = []
    attempts: list[dict] = []
    history: list[dict] = []
    assignments: list[dict] = []


class ProductResponse(BaseModel):
    """A single shop product item."""

    id: int
    title: str
    slug: str = ""
    description: str = ""
    price: float = 0.0
    sale_price: Optional[float] = None
    image_url: Optional[str] = None
    category: str = ""
    rating: float = 0.0
    stock_status: str = "in_stock"
    is_active: bool = True


class MenuItemResponse(BaseModel):
    """A single navigation menu item."""

    id: int
    parent_id: Optional[int] = None
    title: str
    link: str
    menu_class: str = ""
    badge: str = ""
    badge_class: str = ""
    icon: str = ""
    sort_order: int = 0
    is_active: bool = True


class MenuGroupResponse(BaseModel):
    """A menu group containing heading and child items."""

    title: str
    children: list[MenuItemResponse] = []
