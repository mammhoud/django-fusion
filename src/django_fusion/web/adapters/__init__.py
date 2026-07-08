"""
Adapters module for django_fusion.

Provides authentication and integration adapters for Django applications.
This module contains adapter classes that extend or customize third-party
library behavior while maintaining compatibility with django-fusion patterns.

Classes:
    AccountAdapter: Enhanced allauth adapter with invitation system support.
    SocialAccountAdapter: Social account adapter with invitation integration.

The adapters follow the adapter pattern to provide a consistent interface
over third-party authentication libraries while maintaining django-fusion
separation of concerns.
"""

from .account import AccountAdapter
from .social import SocialAccountAdapter

__all__ = [
    "AccountAdapter",
    "SocialAccountAdapter",
]
