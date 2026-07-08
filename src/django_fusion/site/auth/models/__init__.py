"""
Authentication models for django_fusion.

Provides generic user authentication models including roles and tokens.

Modules:
- role: Role model for user roles and permissions
- token: Token model for authentication tokens
"""

from .role import Role
from .token import Token

__all__ = [
    "Role",
    "Token",
]
