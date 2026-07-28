"""
Email template utilities for fusion-cms.com.

Delegates to django_fusion.handlers.core
"""

from django_fusion.core.handlers import EmailTemplateRegistry, EmailTemplateSelector

__all__ = ["EmailTemplateSelector", "EmailTemplateRegistry"]
