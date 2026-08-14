"""
Contact API schemas — Form submission (Pydantic).

Endpoints:
    POST /apis/contact/submit  → ContactResponse (201)
"""

from __future__ import annotations

from pydantic import BaseModel


class ContactRequest(BaseModel):
    """POST /apis/contact/submit request body."""

    name: str
    email: str
    subject: str
    message: str


class ContactResponse(BaseModel):
    """Successful contact submission response."""

    status: str = "ok"
    id: int = 0
    message: str = "Thank you for your message."
