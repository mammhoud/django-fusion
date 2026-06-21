"""Compatibility imports for allauth views moved to `accounts.views.allauth`."""

from .views.allauth import AllauthLoginView, AllauthSignupView

__all__ = ["AllauthLoginView", "AllauthSignupView"]
