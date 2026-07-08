"""
Filters module for django_fusion.

Provides filter classes for querying and validating data in Django applications.
Supports dictionary-based, token-aware, and cached filter methods.

Classes:
    BaseFilterMethod: Base class for all filter methods.
    DictFilterMethod: Filter method using dictionary-based configuration.
    UniversalFilter: Universal filter supporting multiple filter strategies.
    TokenFilterMixin: Mixin for token-aware filtering.
    TokenAwareFilter: Filter class with token-based access control.
    CachedBaseFilterMethod: Cached version of BaseFilterMethod.
    CachedDictFilterMethod: Cached version of DictFilterMethod.
    UniqueFieldValidator: Validator ensuring field uniqueness.
    SlugFieldValidator: Validator for slug field format and uniqueness.
"""

from .base import BaseFilterMethod, DictFilterMethod, UniversalFilter
from .cache import CachedBaseFilterMethod, CachedDictFilterMethod
from .token import TokenAwareFilter, TokenFilterMixin
from .validators import SlugFieldValidator, UniqueFieldValidator

__all__ = [
    'BaseFilterMethod',
    'DictFilterMethod',
    'UniversalFilter',
    'TokenFilterMixin',
    'TokenAwareFilter',
    'CachedBaseFilterMethod',
    'CachedDictFilterMethod',
    'UniqueFieldValidator',
    'SlugFieldValidator',
]
