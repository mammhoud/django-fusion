"""components — Django component system with slot/prop/var template tags.

The ``comp`` package provides a lightweight server-side component model for
Django templates, inspired by Vue SFC and Livewire but rendered server-side
via Django template tags.

Sub-packages
------------
comp.configuration  Component manifest, options schema, and config helpers.
comp.core           Component init and lifecycle (up.py = component bootstrap).
comp.forms          Form layout helpers for component-based form rendering.
comp.fragment.loader        Lazy/HTMX-safe component loader decorator.
comp.management     Management commands (generate_asset_manifest).
comp.payloads       Component payload service (JSON data for HTMX responses).
comp.fragment.plugins        Pluggy-based hook system for extending component behavior.
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
    from django_fusion.comp.fragment.loaders import component_loader
    from django_fusion.comp.payloads.services import ComponentPayloadService
"""
