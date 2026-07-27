"""
Unpoly plugin for django-fusion fragments
=========================================

Provides the ``Unpoly`` request wrapper and Django adapter used to speak the
`Unpoly server protocol <https://unpoly.com/up.protocol>`_.

Usage::

    from django_fusion.plugins.unpoly import Unpoly, DjangoAdapter

    def my_view(request):
        request.up = DjangoAdapter(request)
        request.up.set_title("My Page")
        if request.up.validate:
            ...
"""

from .adapter import BaseAdapter, DjangoAdapter
from .core import Layer, Unpoly

__all__ = [
    "BaseAdapter",
    "DjangoAdapter",
    "Layer",
    "Unpoly",
]
