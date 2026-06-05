"""
Stub/mock implementation of django-osoul for environments where the real package
is not available (e.g., memory constraints).

This module provides all the classes and functions that projects depend on
from django_osoul without requiring the actual package or its dependencies
(like Twilio).
"""

from .models import *  # noqa: F401, F403
from .site import *  # noqa: F401, F403
from .managers import *  # noqa: F401, F403
from .core import *  # noqa: F401, F403

__version__ = "0.1.0"
__doc__ = "Stub package for django-osoul"
