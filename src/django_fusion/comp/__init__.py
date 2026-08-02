"""components — Django component system with slot/prop/var template tags.

The ``comp`` package provides a lightweight server-side component model for
Django templates, inspired by Vue SFC and Livewire but rendered server-side
via Django template tags.

Sub-packages
------------
comp.config        Component manifest, options schema, and config helpers.
comp.core           Component init and lifecycle (up.py = component bootstrap).
comp.forms          Form layout helpers for component-based form rendering.
comp.loader        Lazy/HTMX-safe component loader decorator.
comp.management     Management commands (generate_asset_manifest).
comp.payloads       Component payload service (JSON data for HTMX responses).
comp.plugins       Pluggy-based hook system for extending component behavior.
comp.static         Static file discovery and manifest helpers.
comp.templates      Template discovery, URL registration, and rendering engine.
comp.templatetags   Django template tags: comp, slot, prop, var, css, js,
                    plus UI tags: card, field, menu, modal, table, notification.

Usage::

    # In templates (registered as builtins):
    {% comp "my_component" param1="value" %}
        {% slot "body" %}Content{% endslot %}
    {% endcomp %}

    # In Python:
    from django_fusion.comp.loader import component_loader
    from django_fusion.comp.payloads.services import ComponentPayloadService
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_fusion.comp._init import Component, components

# ``Component`` and ``components`` are available at ``TYPE_CHECKING`` time
# for static analysis only.  At runtime, import directly from ``_init``:
#
#     from django_fusion.comp._init import Component, components
#
# This avoids eagerly parsing ``_init.py`` (which depends on
# ``staticfiles.py``) when importing the package, preventing circular
# import chains.
__all__: list[str] = []
