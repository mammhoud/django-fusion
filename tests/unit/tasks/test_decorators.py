"""Unit tests for tasks/decorators.py — shared_task fallback paths."""

import importlib
import sys
from unittest.mock import patch

import pytest

from configs.tools.worker.decorators import shared_task


class TestSharedTaskWithCelery:
    def test_with_celery_installed_returns_celery_decorator(self):
        # Celery IS installed in the test env, so the real path should work
        result = shared_task(name="test.task")
        assert callable(result)

    def test_with_celery_decorates_function(self):
        @shared_task(name="test.direct")
        def my_func():
            return 42

        # When celery is installed, it wraps the function as a Task
        # The function should still be callable
        assert callable(my_func)


class TestSharedTaskWithoutCelery:
    @patch("configs.tools.worker.decorators.importlib.util.find_spec", return_value=None)
    def test_no_celery_returns_noop_decorator(self, mock_find):
        decorator = shared_task(name="test.task")
        assert callable(decorator)

        def my_func():
            return 99

        result = decorator(my_func)
        assert result is my_func
        assert result() == 99

    @patch("configs.tools.worker.decorators.importlib.util.find_spec", return_value=None)
    def test_no_celery_bare_decorator(self, mock_find):
        def my_func():
            return 7

        result = shared_task(my_func)
        assert result is my_func
        assert result() == 7

    @patch("configs.tools.worker.decorators.importlib.util.find_spec", return_value=None)
    def test_no_celery_with_kwargs_only(self, mock_find):
        decorator = shared_task(name="test.kw", bind=True)
        assert callable(decorator)

        def my_func():
            return 123

        wrapped = decorator(my_func)
        assert wrapped is my_func
