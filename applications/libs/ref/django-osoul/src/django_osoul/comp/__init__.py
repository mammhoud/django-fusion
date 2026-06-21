"""
Component module for django_osoul.

Organized by category:
- core: Core component initialization
- configuration: Component configuration
- static: Static files management
- templates: Template management
"""
from pluggy import HookimplMarker as _HookimplMarker

# hookimpl marker for django_osoul.comp plugins
hookimpl = _HookimplMarker("django_osoul.comp")

from .configuration import *  # noqa: F401, F403
from .core import *  # noqa: F401, F403
from .static import *  # noqa: F401, F403
from .templates import *  # noqa: F401, F403

__all__ = ["hookimpl"]
