"""
Decorator utilities for Django Forge.

Provides common decorators for caching, retrying, and logging.
"""

import functools
import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


def cache_result(timeout: int = 300):
    """
    Decorator to cache function results.

    Args:
        timeout: Cache timeout in seconds (default: 300)

    Returns:
        Decorated function

    Example:
        >>> @cache_result(timeout=600)
        >>> def expensive_operation():
        ...     return "result"
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_time = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from args and kwargs
            key = (args, tuple(sorted(kwargs.items())))

            # Check if cached and not expired
            if key in cache:
                if time.time() - cache_time[key] < timeout:
                    return cache[key]

            # Call function and cache result
            result = func(*args, **kwargs)
            cache[key] = result
            cache_time[key] = time.time()

            return result

        return wrapper

    return decorator


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function on exception.

    Args:
        max_retries: Maximum number of retries (default: 3)
        delay: Initial delay between retries in seconds (default: 1.0)
        backoff: Backoff multiplier for delay (default: 2.0)
        exceptions: Tuple of exceptions to catch (default: (Exception,))

    Returns:
        Decorated function

    Example:
        >>> @retry_on_exception(max_retries=3, delay=1.0)
        >>> def unreliable_operation():
        ...     return "result"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )

            raise last_exception

        return wrapper

    return decorator


def log_execution(level: str = "INFO"):
    """
    Decorator to log function execution.

    Args:
        level: Logging level (default: "INFO")

    Returns:
        Decorated function

    Example:
        >>> @log_execution(level="DEBUG")
        >>> def my_function(x, y):
        ...     return x + y
    """
    def decorator(func: Callable) -> Callable:
        log_func = getattr(logger, level.lower(), logger.info)

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            log_func(f"Executing {func.__name__} with args={args}, kwargs={kwargs}")

            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                log_func(f"Completed {func.__name__} in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Failed {func.__name__} after {elapsed:.2f}s: {e}")
                raise

        return wrapper

    return decorator
