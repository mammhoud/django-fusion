"""
Project-local shim to expose `components` tag library under
`plugins.accounts` so templates using `{% load components %}` resolve.
It re-exports the `register` from django_osoul's components module.
"""
from importlib import import_module

try:
    _mod = import_module("django_osoul.comp.templatetags.components")
    register = _mod.register
except Exception:  # pragma: no cover
    from django import template

    register = template.Library()
