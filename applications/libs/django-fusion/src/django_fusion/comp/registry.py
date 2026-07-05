"""Dynamic include-path → component-path registration.

This module bridges Django's ``{% include "path" %}`` world and
``django_fusion``'s ``{% comp "name" %}`` world for cases where the
existing template file IS the component (no separate component
subdirectory / module needed).

The base :class:`ComponentRegistry` resolves component names lazily on
first ``get_component(name)`` call, so a fresh project does not need
this module at all to render ``{% comp "partials/auth_buttons.html" %}``
correctly. This module exists for sites that want **eager pre-warming**:

* to surface "missing template" errors at startup rather than at first
  render-time,
* to control ``Component.name`` so it matches the registry key verbatim
  (drop-in equivalent to ``{% include %}``),
* to register many named paths from a list in their site's
  ``AppConfig.ready()``.

Public API
----------
- :func:`register_include_path` — pre-register a single include path.
- :func:`register_include_paths` — bulk version; returns the list of
  successfully-cached keys.
- :func:`discover_under_root` — glob a template root for ``*.html``
  files and register each as a path-style component.
- :func:`register_default_partials` — default partials-path discovery
  wired into ``django_fusion.comp.apps.CoreExtAppConfig.ready()``; sites
  override ``COMPONENTS_INCLUDE_PATH_ROOTS`` in settings to extend.

Caching
-------
Component mappings are cached in Redis when available, falling back to
in-memory caching. Configure via Django's CACHES setting:

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
        }
    }

See :mod:`django_fusion.comp.cache` for details.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Final

from django.template.loader import select_template
from django.template.backends.django import Template as DjangoTemplate

from django_fusion.comp.core._init import Component, components
from django_fusion.comp.cache import get_component_map_cache

logger = logging.getLogger(__name__)


_DEFAULT_INCLUDE_PATH_ROOTS: Final[tuple[str, ...]] = (
    "partials",
    "components",
)


class _LazyIncludeTemplate:
    """Duck-typed ``DjangoTemplate`` wrapper that defers ``select_template``.

    The eager approach (``select_template`` at component-build time) blew
    up at startup when a partial uses a tag library unavailable in the
    current settings — e.g. ``{% load wagtailimages_tags %}`` against a
    minimal ``INSTALLED_APPS`` test bundle. ``BoundComponent.render``
    walks ``self.component.template.template.render(context)``, so we
    expose ``.template`` lazily and lazily resolve the underlying
    ``django.template.backends.django.Template`` only on first access.
    """

    __slots__ = ("path", "_resolved")

    def __init__(self, path: str) -> None:
        self.path = path
        self._resolved: DjangoTemplate | None = None

    def _get_resolved(self) -> DjangoTemplate:
        if self._resolved is None:
            self._resolved = select_template([self.path])
        return self._resolved

    @property
    def template(self) -> "django.template.Template":
        # Expose the INNER ``django.template.Template`` so
        # ``Component.nodelist`` (``self.template.template.nodelist``)
        # and ``BoundComponent.render`` (``self.component.template.template.render``)
        # land on the right object. Returning the outer
        # ``DjangoTemplate`` here puts ``Component`` one level shallower
        # than expected and triggers ``AttributeError: 'Template'
        # object has no attribute 'nodelist'`` on first render.
        return self._get_resolved().template

    def __getattr__(self, name: str):  # for duck-typed DjangoTemplate attrs
        # Forward every attribute access (other than the data slots
        # ``path`` / ``_resolved`` and the ``template`` property above)
        # to the resolved ``DjangoTemplate``. This keeps callers that
        # treat ``_LazyIncludeTemplate`` as a ``DjangoTemplate`` (e.g.
        # legacy code accessing ``.origin`` / ``.engine``) working.
        return getattr(self._get_resolved(), name)


class IncludePathComponent(Component):
    """``Component`` subclass that preserves the include path as ``name``.

    The base ``Component.from_name`` derives ``name`` from the template
    stem when the path's prefix is not under a recognised component
    directory — e.g. ``partials/auth_buttons.html`` becomes
    ``Component("auth_buttons", ...)``. We override here so the registry
    key (``partials/auth_buttons.html``) and the component name match,
    which makes render-history introspection deterministic and matches
    the literal text the user wrote in ``{% comp "partials/auth_buttons.html" %}``.

    Re-declaring ``__slots__`` is required when subclassing a
    ``slots=True`` dataclass: without it the subclass silently falls
    back to ``__dict__`` and breaks the slot layout. The empty tuple
    ``()`` declares "no new slots beyond the parent".
    """

    __slots__ = ()

    @classmethod
    def from_include_path(cls, path: str) -> Component:
        """Build a component registered under the include path verbatim.

        Returns
        -------
        Component
            With ``name = path`` and ``template`` set to a
            :class:`_LazyIncludeTemplate` that defers the actual
            ``select_template([path])`` call until first render.
            This avoids ``TemplateSyntaxError`` at startup when the
            partial references tag libraries (e.g. wagtail) not
            installed in the active settings.
        """
        return cls(name=path, template=_LazyIncludeTemplate(path), assets=frozenset())


def register_include_path(path: str) -> str:
    """Pre-register one template path as a path-style component.

    Raises
    ------
    django.template.exceptions.TemplateDoesNotExist
        If no engine directory resolves ``path``. Re-raised so callers
        detect a missing template at startup rather than silently
        ignoring it (the lazy-fallback path silently returned ``[]``,
        which made ``{% comp "..." %}`` resolve through
        ``Component.from_name`` later and not through the eager cache).

    Returns
    -------
    str
        The registry key under which the component is cached (verbatim
        include path). Useful for logging / chaining.
    """
    if path in components._components:
        return path
    
    components._components[path] = IncludePathComponent.from_include_path(path)
    
    # Cache in Redis/in-memory
    cache = get_component_map_cache()
    cache.set_component(path, path)
    
    logger.debug("Registering include-path component: %s", path)
    return path


def register_include_paths(paths: Iterable[str]) -> list[str]:
    """Bulk version of :func:`register_include_path`.

    Returns
    -------
    list[str]
        Registry keys that exist after the call (excludes paths whose
        template could not be resolved).
    """
    cached: list[str] = []
    cache = get_component_map_cache()
    
    # Batch cache operations
    batch_mapping = {}
    
    for path in paths:
        if path not in components._components:
            try:
                components._components[path] = IncludePathComponent.from_include_path(path)
                cached.append(path)
                batch_mapping[path] = path
            except Exception as e:
                logger.debug(f"Failed to register path {path}: {e}")
        else:
            cached.append(path)
    
    # Batch cache all at once
    if batch_mapping:
        cache.set_components(batch_mapping)
        logger.debug(f"Cached {len(batch_mapping)} component paths")
    
    return cached


def _iter_default_include_path_roots() -> Iterator[Path]:
    """Resolve ``COMPONENTS_INCLUDE_PATH_ROOTS`` (or compile-time default).

    Each entry may be a relative name (``"partials"``) — resolved against
    every template engine dir — or an absolute path. Empty entries are
    skipped silently. Sites subclass / override the default by setting
    ``COMPONENTS_INCLUDE_PATH_ROOTS`` to a tuple of strings after the
    ``django_fusion.comp.apps`` AppConfig is registered.
    """
    from django.conf import settings
    from django.template.utils import get_app_template_dirs

    roots = getattr(
        settings,
        "COMPONENTS_INCLUDE_PATH_ROOTS",
        _DEFAULT_INCLUDE_PATH_ROOTS,
    )
    if not roots:
        return iter(())
    engine_dirs = [Path(d) for d in settings.TEMPLATES[0].get("DIRS", [])]
    for root in roots:
        if not root:
            continue
        root_path = Path(root)
        if root_path.is_absolute():
            yield root_path
            continue
        for engine_dir in engine_dirs:
            yield engine_dir / root_path
        for app_dir in get_app_template_dirs("templates"):
            yield Path(app_dir) / root_path


def discover_under_root(root: str | Path) -> list[str]:
    """Glob ``*.html`` under ``root`` and register each file as a path-style component.

    Missing roots are skipped silently (logged at debug level).
    """
    root_path = Path(root)
    if not root_path.is_dir():
        logger.debug("discover_under_root: %s is not a directory", root_path)
        return []
    paths = sorted(str(p.relative_to(root_path.parent)) for p in root_path.rglob("*.html"))
    return register_include_paths(paths)


def register_default_partials() -> list[str]:
    """Discover and register every include path under configured roots."""
    cached: list[str] = []
    seen: set[str] = set()
    for root in _iter_default_include_path_roots():
        for path in discover_under_root(root):
            if path in seen:
                continue
            seen.add(path)
            cached.append(path)
    return cached
