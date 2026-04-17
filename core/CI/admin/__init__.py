"""
Django admin configuration for core.CI app.

Imports all admin configurations to register them with Django admin.
"""

from .group_admin import *  # noqa: F401, F403
from .invitations import *  # noqa: F401, F403
