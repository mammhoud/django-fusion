"""Compatibility imports for allauth-backed account views.

The view implementations now live in :mod:`plugins.accounts.views.auth`.
Keep this module so existing imports of ``plugins.accounts.allauth_views``
continue to work.
"""

from .views.auth import AllauthLoginView, AllauthSignupView

__all__ = ["AllauthLoginView", "AllauthSignupView"]
