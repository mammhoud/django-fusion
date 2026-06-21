"""
Adapters module for django_osoul.

Provides authentication and integration adapters for Django applications.
This module contains adapter classes that extend or customize third-party
library behavior while maintaining compatibility with django-osoul patterns.

Classes:
    AccountAdapter: Enhanced allauth adapter with invitation system support.
    SocialAccountAdapter: Social account adapter with invitation integration.

The adapters follow the adapter pattern to provide a consistent interface
over third-party authentication libraries while maintaining django-osoul
separation of concerns.
"""

from .account import AccountAdapter
from .social import SocialAccountAdapter

__all__ = [
    "AccountAdapter",
    "SocialAccountAdapter",
]
