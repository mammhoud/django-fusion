"""Celery application for the shared multi-website task worker."""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import sys

logger = logging.getLogger(__name__)


def _configure_default_site() -> None:
    """Prepare the selected website import path before Django settings load."""
    selected = (
        os.getenv("DJANGO_SITE")
        or os.getenv("DJANGO_WEBSITE")
        or os.getenv("WEBSITE")
        or "ctc-research.com"
    )
    try:
        site_module = importlib.import_module("configs.site")
    except (ImportError, ModuleNotFoundError) as exc:
        logger.info("configs.site not available (%s), falling back to default settings", exc)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
        return

    selected = site_module.active_website_name(selected)
    site_module.configure_site_environment(selected)
    for path in (site_module.site_dir_for(selected), site_module.WORKSPACE_DIR):
        path_text = str(path)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


_configure_default_site()

TASK_IMPORTS = (
    "tasks.email",
    "tasks.content",
    "tasks.crafts_ai.rseal",
)

if importlib.util.find_spec("celery") is not None:
    celery_module = importlib.import_module("celery")
    app = celery_module.Celery("structa_shared_tasks")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.conf.imports = TASK_IMPORTS
    app.autodiscover_tasks(lambda: ["tasks"])
else:
    class _MissingCeleryApp:
        main = "structa_shared_tasks"
        conf = {"imports": TASK_IMPORTS}

        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    app = _MissingCeleryApp()
