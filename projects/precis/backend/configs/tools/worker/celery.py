"""Celery application for the Precis/LMS task worker.

Bootstrap module that creates the Celery app instance (``app``) used
by the ``shared-scheduler`` container for celery-beat scheduling.

On import, this module:
1. Detects and configures the target website environment via
   :func:`_configure_default_site` so Django settings are available
   before Celery's ``config_from_object`` call.
2. Creates the Celery ``app`` instance configured from Django settings
   (``CELERY_`` namespace) with autodiscovery pointed at ``configs.tools.worker``.
3. Falls back to a no-op ``_MissingCeleryApp`` when Celery is not
   installed, allowing imports in Dramatiq-only deployments.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import sys

logger = logging.getLogger(__name__)


def _configure_default_site() -> None:
    """Prepare the selected website import path before Django settings load.

    Called at module import time to seed environment variables and
    ``sys.path`` before the Celery app reads Django settings. This
    ensures ``django.conf:settings`` resolves correctly when Celery
    calls ``config_from_object("django.conf:settings", ...)``.

    Resolution order:
    1. ``DJANGO_SITE`` env var
    2. ``DJANGO_WEBSITE`` env var
    3. ``WEBSITE`` env var
    4. Fallback to the configured Precis/LMS default

    If the Precis-local ``configs.site`` is not importable (for example during
    a lightweight test),
    falls back to setting ``DJANGO_SETTINGS_MODULE=settings`` and
    returns without further configuration.
    """
    requested = (
        os.getenv("DJANGO_SITE")
        or os.getenv("DJANGO_WEBSITE")
        or os.getenv("WEBSITE")
    )
    try:
        site_module = importlib.import_module("configs.site")
    except (ImportError, ModuleNotFoundError) as exc:
        logger.info("configs.site not available (%s), falling back to default settings", exc)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
        return

    selected = (
        site_module.site_config(requested)["name"]
        if requested
        else site_module.active_website_name("lms-fusion")
    )
    site_module.configure_site_environment(selected)
    for path in (site_module.site_dir_for(selected), site_module.WORKSPACE_DIR):
        path_text = str(path)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


_configure_default_site()

# Shared task actors live in configs.tools.worker. Celery is kept only for
# the django-celery-beat scheduler and Precis/LMS Celery tasks.
TASK_IMPORTS = ()

if importlib.util.find_spec("celery") is not None:
    celery_module = importlib.import_module("celery")
    app = celery_module.Celery("structa_shared_tasks")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.conf.imports = TASK_IMPORTS
    app.autodiscover_tasks(lambda: ["configs.tools.worker"])
else:
    class _MissingCeleryApp:
        main = "structa_shared_tasks"
        conf = {"imports": TASK_IMPORTS}

        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    app = _MissingCeleryApp()
