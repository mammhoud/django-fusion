"""Compatibility exports for legacy ``django_osoul.models`` imports."""

from __future__ import annotations

from django_osoul.core.models.base import BaseModel, TimeStampedModel, UUIDModel
from django_osoul.core.models.email import EmailLog, EmailTemplate, UserGroup

DefaultBase = BaseModel

__all__ = [
    "BaseModel",
    "DefaultBase",
    "EmailLog",
    "EmailTemplate",
    "TimeStampedModel",
    "UserGroup",
    "UUIDModel",
]
