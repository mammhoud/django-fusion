"""VResume email service — re-exports the canonical shared EmailService.

VResume previously shipped a smaller shim with only ``send`` and
``send_simple`` methods; adopting the shared class also exposes ``queue``
plus the convenience methods (``send_welcome``, ``send_password_reset``,
``send_enrollment_confirmation``, ``send_course_completion``).

The class lives in ``applications/www/projects/services/email/service.py``;
this module is kept so existing imports such as
``from pages.connect.services.email import EmailService`` keep resolving.
"""

from __future__ import annotations

from applications.www.core.services.email.service import EmailService
from applications.www.core.services.email.service import email_service

__all__ = ["EmailService", "email_service"]

