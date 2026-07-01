"""Compatibility shim — ``django_osoul.smart_loader`` is now ``django_osoul.comp.loaders``.

Import from the canonical path instead::

    from django_osoul.comp.loaders import component_loader
"""
from __future__ import annotations
from django_osoul.comp.loaders import component_loader  # noqa: F401

__all__ = ["component_loader"]
