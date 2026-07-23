"""
Authentication module for django_fusion.

Provides generic authentication utilities, mixins, forms, adapters, and models.

Submodules:
- mixins: Core authentication mixins (AuthConfig, AuthBaseMixin, AuthValidatorMixin, AuthProcessorMixin)
- forms: Authentication forms (login, signup, password reset, etc.)
- adapters: Authentication adapters (social auth, etc.)
- models: Authentication models (Role, Token)

Usage:
    from django_fusion.contrib.auth import AuthConfig, AuthProcessorMixin
    from django_fusion.contrib.auth.forms import LoginForm, SignupForm
    from django_fusion.contrib.auth.adapters import SocialAccountAdapter
    from django_fusion.contrib.auth.models import Role, Token
"""

from .mixins import AuthBaseMixin, AuthConfig, AuthProcessorMixin, AuthValidatorMixin
from .models import Role, Token

__all__ = [
    "AuthConfig",
    "AuthBaseMixin",
    "AuthValidatorMixin",
    "AuthProcessorMixin",
    "Role",
    "Token",
]
