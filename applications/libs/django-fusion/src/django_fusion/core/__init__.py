"""Core layer — foundational models, managers, filters, services, and middleware.

Sub-packages
------------
core.cache          Pluggable cache manager base classes (CachedManager).
core.filters        Queryset filters: token, revision, cache-aware filters.
core.handlers       View handler base classes and HTMX mixins (fragment, search).
  .mixins           Per-concern mixins: cache, fragment, page, search, token.
core.managers       Django model managers: role hierarchy, group access, tags, user.
core.middlewares    Request middleware: error tracker, privacy, language, freeze.
core.models         Base model classes, auth, email, and interaction models.
  .interaction      Call and notification interaction models.
core.services       Service layer: CRUD base, cart, person services.
core.utils          Utility functions: data, formatting, security helpers.
  .data             Cache helpers, datetime utils, response wrappers.
  .formatting       Text formatters, decorator utilities.
  .security         Token generation, input validation, validators.

Primary exports::

    from django_fusion.core.models.base import BaseModel, TimeStampedModel, UUIDModel
    from django_fusion.core.managers import BaseManager, RoleHierarchyManager
    from django_fusion.core.services.base import BaseService
    from django_fusion.core.cache import CachedManager
"""
