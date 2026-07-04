"""Django settings for running site-specific template tests from applications/.

This module re-exports the workspace ``tests/settings.py`` and adds the
``applications/assets/templates/`` directory to ``TEMPLATES.DIRS`` so that
shared templates (e.g. ``events.html``) are discoverable when pytest is run
from ``applications/`` via ``make test-local`` (which is ``uv run pytest``).

Background
----------
``applications/pyproject.toml`` pins ``DJANGO_SETTINGS_MODULE = "tests.settings"``
and sets ``testpaths = ["tests", "libs/django-osoul/tests/analyzer"]``.
When pytest is run from ``applications/``, the ``tests`` testpath resolves to
``applications/tests/`` (a directory that did not exist before this shim), and
``tests.settings`` resolves to this module.

The root ``tests/settings.py`` (at the workspace root) holds the full Django
configuration for the library test corpus (django-osoul analyzer, ceptor-ai,
etc.). Site-specific tests need the same base but with the shared
``applications/assets/templates/`` directory added to ``TEMPLATES.DIRS`` so
that templates like ``events.html`` (which include ``events/includes/events_grid.html``)
are discoverable without booting the full LMS Django settings module.
"""
import importlib.util as _importlib_util
import sys
from pathlib import Path

# Add the workspace root to sys.path so we can load the root tests.settings
# without colliding with this local module.
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Load the root settings by file path to avoid name collision with this module.
_spec = _importlib_util.spec_from_file_location(
    "_root_tests_settings",
    str(_root / "tests" / "settings.py"),
)
_root_settings = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(_root_settings)

# Re-export all public attributes from the root settings.
for _attr in dir(_root_settings):
    if not _attr.startswith("_"):
        globals()[_attr] = getattr(_root_settings, _attr)

# Add the shared applications/assets/templates/ to TEMPLATES.DIRS so shared
# templates (e.g. events.html, events/main.html, events/includes/events_grid.html)
# are discoverable when running tests from applications/.
_apps_dir = Path(__file__).resolve().parent.parent
TEMPLATES[0]["DIRS"].append(str(_apps_dir / "assets" / "templates"))
