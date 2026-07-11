"""Shared background task project for all websites."""

from .celery import app as celery_app

__all__ = ["celery_app"]
