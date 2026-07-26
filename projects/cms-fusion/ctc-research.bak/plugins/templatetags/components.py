"""
Shim tag library to expose `components` under the project `plugins` app so
templates that use `{% load components %}` continue to work. This re-exports
the `register` instance from `django_fusion.comp.templatetags.components`.
"""
from importlib import import_module

try:
    _mod = import_module("django_fusion.comp.templatetags.components")
    register = _mod.register
except Exception:  # pragma: no cover - fallback to empty register
    from django import template

    register = template.Library()
