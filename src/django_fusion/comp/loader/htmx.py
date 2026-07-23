"""HTMX smart component loader."""
from __future__ import annotations

import concurrent.futures
import functools
import logging
from pathlib import Path
from typing import Callable

from django.conf import settings
from django.template.loader import render_to_string


def _slow_logger() -> logging.Logger:
    log_dir = Path(getattr(settings, "BASE_DIR", Path.cwd())) / "applications" / "logs" / "components"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler_path = log_dir / "slow_components.log"
    logger = logging.getLogger("django_fusion.fragments.slow")
    if not logger.handlers:
        handler = logging.FileHandler(handler_path)
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        logger.addHandler(handler); logger.setLevel(logging.INFO); logger.propagate = False
    return logger


def component_loader(timeout: float = 0.5, loader_template: str = "components/loader.html"):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    _slow_logger().warning("Slow component %s exceeded %.3fs", func.__qualname__, timeout)
                    return render_to_string(loader_template, {"component_name": func.__name__, "timeout": timeout})
        return wrapper
    return decorator
