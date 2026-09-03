"""
django_fusion.builder
=====================

The landing builder — Wagtail page assembly from the shared ``fu-*``
component catalog, with theme picking and dynamic template fields.

Products subclass the abstract
:class:`~django_fusion.builder.models.BuilderPage` in their own app, add
``django_fusion.builder`` to ``INSTALLED_APPS``, and wire the API views
(``django_fusion.builder.api``) under their own URL prefix.

See ``django_fusion/builder/docs/`` for the guide.

Importing this package must not import Wagtail models: Django imports the
package ``__init__`` before the app registry is populated, so eager model
imports break ``manage.py`` startup. Import ``BuilderPage`` from
``django_fusion.builder.models`` directly.
"""

__all__: list[str] = []
