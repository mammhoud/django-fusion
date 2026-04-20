"""
Email template utilities for ctc-research.com.

Delegates to django_osoul.handlers.core
"""

from django_osoul.handlers.core import EmailTemplateRegistry, EmailTemplateSelector

__all__ = ["EmailTemplateSelector", "EmailTemplateRegistry"]
