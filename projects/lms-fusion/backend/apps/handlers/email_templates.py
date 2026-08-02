"""
Email template utilities for fusion-cms.com.

Uses django-fusion's canonical email template handlers.
"""

from django_fusion.management.handlers.emails import EmailTemplateRegistry, EmailTemplateSelector

__all__ = ["EmailTemplateSelector", "EmailTemplateRegistry"]
