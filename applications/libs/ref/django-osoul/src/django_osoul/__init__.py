"""
django_osoul — Django Foundation Layer
=======================================

Pure Django/Python primitives with **no application-layer dependencies**.
Only depends on Django ≥ 4.0 and the Python standard library.

Package structure follows clean architecture with ~7 items per directory:

comp/           — Component framework (configuration, templatetags, forms,
                  payloads, plugins, static)
config/         — Django settings helpers, constants, logging
contrib/        — Contributed modules (admin, debug_tools, email_config,
                  privacy, enums)
core/           — Foundation layer (models, managers, filters, forms,
                  handlers, middlewares, services, utils)
infrastructure/ — Management commands, scripts, translations, template tags
site/           — Site framework (auth, routes, views, context, responses,
                  schemas, paginators)
web/            — Web layer (views, routes, adapters, backends, rendering)

Boundary rule
-------------
``django_osoul`` **must not** import from ``wagtail``, ``celery``,
``django_q``, ``openai``, ``anthropic``, ``faker``, ``mcp``, or
``django_rseal``.
"""

__version__ = "0.1.0"
__author__ = "Mahmoud"
__license__ = "MIT"

# Models are imported lazily to avoid AppRegistryNotReady errors
# when this package is imported before django.setup() is called.

def __getattr__(name):
    _model_exports = {
        "BaseModel", "TimeStampedModel", "UUIDModel",
        "AuditMixin", "SoftDeleteMixin", "SoftDeleteModel",
        "StatusMixin", "TimestampedModel", "UUIDPrimaryKeyModel",
    }
    _adapter_exports = {
        "AccountAdapter", "SocialAccountAdapter",
    }

    if name in _model_exports:
        from .core.models.base import BaseModel, TimeStampedModel, UUIDModel
        from .core.models.mixins import (
            AuditMixin,
            SoftDeleteMixin,
            SoftDeleteModel,
            StatusMixin,
            TimestampedModel,
            UUIDPrimaryKeyModel,
        )
        return locals()[name]

    if name in _adapter_exports:
        if name == "AccountAdapter":
            from .web.adapters.account import AccountAdapter
            return AccountAdapter
        elif name == "SocialAccountAdapter":
            from .web.adapters.social import SocialAccountAdapter
            return SocialAccountAdapter

    raise AttributeError(f"module 'django_osoul' has no attribute {name!r}")

__all__ = [
    # base models
    "BaseModel",
    "TimeStampedModel",
    "UUIDModel",
    # mixins
    "TimestampedModel",
    "SoftDeleteModel",
    "UUIDPrimaryKeyModel",
    "SoftDeleteMixin",
    "AuditMixin",
    "StatusMixin",
    # adapters
    "AccountAdapter",
    "SocialAccountAdapter",
]
