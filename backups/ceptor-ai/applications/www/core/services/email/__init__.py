"""Shared ``www.core.services.email`` subpackage."""

from __future__ import annotations

from .service import EmailService
from .service import email_service as email_service

__all__ = ["EmailService", "email_service"]
