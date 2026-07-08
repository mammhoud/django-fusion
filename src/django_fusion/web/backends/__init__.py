"""
django_fusion.backends — authentication backends.

This module provides custom Django authentication backends that extend
the default functionality to support alternative authentication methods.

Classes:
    EmailOrUsernameModelBackend: Authentication backend that accepts
        either email or username for login.

The backends follow Django's authentication backend interface and can
be used as drop-in replacements or additions to the default authentication.
"""
from .auth import EmailOrUsernameModelBackend  # noqa: F401

__all__ = ["EmailOrUsernameModelBackend"]
