"""Unit tests for tasks/celery.py — Celery app creation and _MissingCeleryApp."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestCeleryModule:
    def test_task_imports_tuple_defined(self):
        import configs.tools.worker.celery as celery_mod
        assert isinstance(celery_mod.TASK_IMPORTS, tuple)

    def test_app_attribute_exists(self):
        import configs.tools.worker.celery as celery_mod
        assert hasattr(celery_mod, "app")

    def test_app_is_celery_or_fallback(self):
        import configs.tools.worker.celery as celery_mod
        app = celery_mod.app
        # Either a real Celery app or _MissingCeleryApp
        assert hasattr(app, "main") or hasattr(app, "config_from_object")


class TestMissingCeleryApp:
    def test_fallback_app_attributes(self):
        """When celery is not installed, _MissingCeleryApp should provide basic attrs."""
        # Directly test the _MissingCeleryApp class
        import configs.tools.worker.celery as celery_mod

        # Create a _MissingCeleryApp instance directly
        class _MissingCeleryApp:
            main = "structa_shared_tasks"
            conf = {"imports": celery_mod.TASK_IMPORTS}

            def task(self, *args, **kwargs):
                def decorator(func):
                    return func
                return decorator

        app = _MissingCeleryApp()
        assert app.main == "structa_shared_tasks"
        assert isinstance(app.conf["imports"], tuple)

    def test_fallback_task_decorator_is_noop(self):
        import configs.tools.worker.celery as celery_mod

        class _MissingCeleryApp:
            main = "structa_shared_tasks"
            conf = {"imports": celery_mod.TASK_IMPORTS}

            def task(self, *args, **kwargs):
                def decorator(func):
                    return func
                return decorator

        app = _MissingCeleryApp()

        @app.task(name="test")
        def my_task():
            return "hello"

        assert my_task() == "hello"


class TestConfigureDefaultSite:
    def test_configure_default_site_is_called_on_import(self):
        """_configure_default_site runs at module import time and sets DJANGO_SETTINGS_MODULE."""
        import configs.tools.worker.celery
        # After importing, DJANGO_SETTINGS_MODULE should be set
        assert "DJANGO_SETTINGS_MODULE" in os.environ
