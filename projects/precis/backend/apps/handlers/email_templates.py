"""
Email template utilities for lms-fusion.com.

Uses django-fusion's canonical email template handlers.
"""

from django_fusion.management.handlers.emails import EmailTemplateRegistry, EmailTemplateSelector

__all__ = ["EmailTemplateSelector", "EmailTemplateRegistry"]
