"""Compatibility exports for legacy ``django_osoul.services`` imports."""

from django_osoul.core.handlers.tagging import PostFilterServiceBase, TagServiceBase
from django_osoul.core.services.cart import CartServiceBase

__all__ = ["CartServiceBase", "PostFilterServiceBase", "TagServiceBase"]
