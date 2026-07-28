"""
Email template utilities for structa.cloud.

Delegates to django_fusion.handlers.core
"""

from django_fusion.core.handlers.core import EmailTemplateRegistry, EmailTemplateSelector

__all__ = ["EmailTemplateSelector", "EmailTemplateRegistry"]
