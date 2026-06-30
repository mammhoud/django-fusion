"""
Custom exceptions for Django RSeal.

RSeal-specific exceptions are defined locally.

Canonical imports::
    from ceptor_ai.exceptions import EmailSendError
    from ceptor_ai.exceptions import TemplateNotFoundError
    from ceptor_ai.exceptions import WorkflowError
    from ceptor_ai.exceptions import AIIntegrationError
    from ceptor_ai.exceptions import TaskExecutionError
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
