"""CTC static-file finder customizations.

Unfold intentionally overrides two Django admin JavaScript files. Django's
standard app-directory finder discovers both copies and collectstatic reports a
warning even though the first (Unfold) copy is the desired one. Keep all other
Django admin assets available while omitting only those overridden files from
the standard admin package.
"""

from __future__ import annotations

from pathlib import Path

from django.contrib.staticfiles.finders import AppDirectoriesFinder


class CtcAppDirectoriesFinder(AppDirectoriesFinder):
    """App finder that removes only known Unfold/Django admin collisions."""

    _DJANGO_ADMIN_STATIC_SUFFIX = "/django/contrib/admin/static"
    _UNFOLD_OVERRIDES = frozenset(
        {
            "admin/js/actions.js",
            "admin/js/admin/RelatedObjectLookups.js",
        }
    )

    def list(self, ignore_patterns):
        """Yield app static files without duplicate Unfold admin overrides."""
        for app_name, storage in self.storages.items():
            if not storage.exists(""):
                continue
            is_django_admin = (
                app_name == "django.contrib.admin"
                or Path(storage.location).as_posix().endswith(
                    self._DJANGO_ADMIN_STATIC_SUFFIX
                )
            )
            for path in self._iter_storage_files(storage, ignore_patterns):
                if is_django_admin and path in self._UNFOLD_OVERRIDES:
                    continue
                yield path, storage

    @staticmethod
    def _iter_storage_files(storage, ignore_patterns):
        """Use Django's normal file traversal for one app storage."""
        from django.contrib.staticfiles import utils

        yield from utils.get_files(storage, ignore_patterns)
