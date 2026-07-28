"""
Enrollment API schemas — Enrollment create, list, payment init (Pydantic).

Endpoints:
    POST /apis/enrollments                     → EnrollmentResponse
    GET  /apis/students/<pk>/enrollments       → MyEnrollmentsResponse
    POST /apis/enrollments/<pk>/payment/init   → PaymentInitResponse
    GET  /apis/enrollments/<pk>/progress       → list[ProgressEntryResponse]
    POST /apis/enrollments/<pk>/progress       → ProgressEntryResponse
    GET  /apis/students/<pk>/dashboard         → DashboardDataResponse
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class EnrollmentResponse(BaseModel):
    """A single enrollment record."""

    id: int
    student: int
    course: int
    course_title: str = ""
    course_thumbnail: Optional[str] = None
    price: float = 0.0
    progress: float = 0.0
    status: str = "active"
    payment_status: str = "pending"
    payment_transaction_id: Optional[int] = None
    enrolled_at: str = ""
    completed_at: Optional[str] = None
    is_completed: bool = False
    instructor_name: str = ""
    duration: str = ""


class CreateEnrollmentRequest(BaseModel):
    """POST /apis/enrollments request body."""

    course_id: int


class MyEnrollmentsResponse(BaseModel):
    """List of enrollments for the authenticated user."""

    data: list[EnrollmentResponse]


class ProgressEntryResponse(BaseModel):
    """A single lesson progress entry."""

    id: int
    lesson: int
    lesson_title: str = ""
    is_completed: bool = False
    completed_at: Optional[str] = None
    time_spent: int = 0


class ProgressUpdateRequest(BaseModel):
    """POST /apis/enrollments/<pk>/progress request body."""

    lesson_id: int
    time_spent: int = 0


class DashboardDataResponse(BaseModel):
    """Student dashboard aggregated data."""

    enrolled_courses: int = 0
    active_courses: int = 0
    completed_courses: int = 0
    total_hours: float = 0.0
    recent_activity: list[dict] = []
    upcoming_deadlines: list[dict] = []


class PaymentInitRequest(BaseModel):
    """POST /apis/enrollments/<pk>/payment/init request body."""

    provider: str = "stripe"
    success_url: str = ""
    cancel_url: str = ""


class PaymentInitResponse(BaseModel):
    """Payment initialization response."""

    success: bool = True
    transaction_id: int
    provider: str
    amount: float
    currency: str = "USD"
    redirect_url: Optional[str] = None
    client_secret: Optional[str] = None
    payment_url: Optional[str] = None
    metadata: dict = {}


class PaymentVerifyRequest(BaseModel):
    """POST /apis/payments/<tx_id>/verify request body.

    Currently empty — all params are in the URL.  Reserved for
    future provider-specific override tokens (e.g. PayPal PayerID).
    """
    pass


class PaymentVerifyResponse(BaseModel):
    """Payment verification response."""

    success: bool
    status: str  # "completed" | "failed"
    message: str
    transaction_id: int
    enrollment_id: Optional[int] = None
    course_title: str = ""
    metadata: dict = {}
