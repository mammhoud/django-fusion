"""
Email template utilities for structa.cloud.

Delegates to django_osoul.handlers.core
"""

from django_osoul.core.handlers.core import EmailTemplateRegistry, EmailTemplateSelector

__all__ = ["EmailTemplateSelector", "EmailTemplateRegistry"]
