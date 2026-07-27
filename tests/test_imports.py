"""Smoke tests for canonical public import paths."""


def test_middleware_imports():
    """ErrorTrackerMiddleware is importable from core middlewares."""
    from django_fusion.core.middlewares.error_tracker import (
        ErrorTrackerMiddleware,
    )
    from django_fusion.core.middlewares import (
        ErrorTrackerMiddleware as Middleware,
    )

    assert ErrorTrackerMiddleware is Middleware
