"""Canonical route implementations organized by responsibility.

Import route classes and helpers from their concrete modules:

* ``django_fusion.routes.core.base`` — base viewsets, routes, and descriptors
* ``django_fusion.routes.core.sites`` — ``Site`` and ``Application``
* ``django_fusion.routes.components`` — routable and fragment components
* ``django_fusion.routes.models`` — model viewsets and CRUD mixins
* ``django_fusion.routes.pages`` — page handlers and pagination views
* ``django_fusion.routes.http`` — request detection, responses, notifications
* ``django_fusion.routes.rendering`` — renderers, sessions, template resolution

This package intentionally defines no aggregate exports or compatibility
aliases. Concrete imports keep dependency direction explicit and avoid a
second route API surface.
"""
