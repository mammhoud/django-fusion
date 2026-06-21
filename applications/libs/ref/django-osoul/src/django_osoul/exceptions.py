"""
Custom exceptions for Django Forge.

Provides application-specific exception classes.
"""

from django.core.management.base import CommandError


class ForgeException(Exception):
    """Base exception for Django Forge."""


class ValidationError(ForgeException):
    """Raised when validation fails."""


class NotFoundError(ForgeException):
    """Raised when a resource is not found."""


class PermissionDeniedError(ForgeException):
    """Raised when user lacks required permissions."""


class ConfigurationError(ForgeException):
    """Raised when configuration is invalid."""


class IntegrationError(ForgeException):
    """Raised when external integration fails."""


class TimeoutError(ForgeException):
    """Raised when operation times out."""


class RateLimitError(ForgeException):
    """Raised when rate limit is exceeded."""


class DuplicateError(ForgeException):
    """Raised when duplicate resource exists."""


class InvalidStateError(ForgeException):
    """Raised when object is in invalid state."""


class SeederException(Exception):
    """Raised when seeding operations fail."""


class SeederCommandError(CommandError):
    """Raised when a seeder management command fails."""
