"""
Custom exceptions for Django RSeal.

RSeal-specific exceptions are defined locally.

Canonical imports::
    from django_rseal.exceptions import EmailSendError
    from django_rseal.exceptions import TemplateNotFoundError
    from django_rseal.exceptions import WorkflowError
    from django_rseal.exceptions import AIIntegrationError
    from django_rseal.exceptions import TaskExecutionError
"""


class RSealException(Exception):
    """Base exception for Django RSeal."""


class EmailSendError(RSealException):
    """Raised when email sending fails."""


class TemplateNotFoundError(RSealException):
    """Raised when email template is not found."""


class WorkflowError(RSealException):
    """Raised when workflow execution fails."""


class AIIntegrationError(RSealException):
    """Raised when AI integration fails."""


class TaskExecutionError(RSealException):
    """Raised when task execution fails."""


__all__ = [
    # RSeal-specific
    "RSealException",
    "EmailSendError",
    "TemplateNotFoundError",
    "WorkflowError",
    "AIIntegrationError",
    "TaskExecutionError",
]
