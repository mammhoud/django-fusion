"""Compatibility exports for moved account service modules.

Services for the LMS demo accounts plugin live in ``plugins.accounts.services``.
This package preserves the older ``plugins.accounts.management.services`` import
path used by commands, tests, and shared code.
"""

from ...services import *  # noqa: F401, F403
