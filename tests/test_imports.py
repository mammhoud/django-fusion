"""Smoke tests for canonical public import paths."""


def test_middleware_imports():
    """ErrorTrackerMiddleware is importable from infrastructure middlewares."""
    from django_fusion.infrastructure.middlewares.error_tracker import (
        ErrorTrackerMiddleware,
    )
    from django_fusion.infrastructure.middlewares import (
        ErrorTrackerMiddleware as Middleware,
    )

    assert ErrorTrackerMiddleware is Middleware
