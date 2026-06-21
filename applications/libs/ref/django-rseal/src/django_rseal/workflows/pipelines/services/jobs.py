"""Compatibility stub for django_rseal.pipelines.services.jobs"""
import logging

logger = logging.getLogger(__name__)


def dispatch_job(func, *args, **kwargs):
    """Compatibility stub — runs the job synchronously."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"dispatch_job error: {e}")
        return None
