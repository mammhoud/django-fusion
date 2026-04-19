"""
Utilities module for Django Seed.

This module provides utility functions and helpers for the Django Seed package.
"""

import json
import pickle
import hashlib
import inspect
import logging
import time
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
import re

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class JSONEncoder(DjangoJSONEncoder):
    """Extended JSON encoder for Django Seed."""

    def default(self, obj):
        """Convert objects to JSON-serializable format."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, timedelta):
            return obj.total_seconds()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


def to_json(obj: Any, indent: Optional[int] = None) -> str:
    """Convert an object to JSON string."""
    return json.dumps(obj, cls=JSONEncoder, indent=indent)


def from_json(json_str: str) -> Any:
    """Parse JSON string to Python object."""
    return json.loads(json_str)


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def generate_hash(data: Any) -> str:
    """Generate a hash for data."""
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    else:
        data_bytes = pickle.dumps(data)

    return hashlib.sha256(data_bytes).hexdigest()


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}m {seconds}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None
):
    """Decorator for retrying function calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt == max_attempts:
                        if logger:
                            logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise

                    if logger:
                        logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {current_delay}s...")

                    time.sleep(current_delay)
                    current_delay *= backoff

            # This should never be reached
            raise RuntimeError("Max retry attempts exceeded")

        return wrapper
    return decorator


def timeit(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        return result

    return wrapper


def memoize(ttl: Optional[int] = None):
    """Decorator to memoize function results."""
    cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = (func.__name__, args, frozenset(kwargs.items()))

            # Check cache
            if key in cache:
                value, timestamp = cache[key]
                if ttl is None or (time.time() - timestamp) < ttl:
                    return value

            # Not in cache or expired, compute
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result

        return wrapper
    return decorator


def get_class_name(obj: Any) -> str:
    """Get the class name of an object."""
    if hasattr(obj, '__class__'):
        return obj.__class__.__name__
    return type(obj).__name__


def get_function_signature(func: Callable) -> str:
    """Get the signature of a function."""
    return str(inspect.signature(func))


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries."""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(obj: Any, *keys, default: Any = None) -> Any:
    """Safely get nested attributes or dictionary keys."""
    current = obj

    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        elif hasattr(current, key):
            current = getattr(current, key)
        else:
            return default

        if current is None:
            return default

    return current


def is_valid_uuid(uuid_str: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False


def convert_to_datetime(value: Any) -> Optional[datetime]:
    """Convert various formats to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            pass
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    return None


# Type conversion utilities
def to_int(value: Any, default: int = 0) -> int:
    """Convert value to integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    """Convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def to_bool(value: Any, default: bool = False) -> bool:
    """Convert value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on')
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def to_str(value: Any, default: str = '') -> str:
    """Convert value to string."""
    if value is None:
        return default
    return str(value)
