"""Compatibility shim — ``ceptor_ai.seeder`` is now ``ceptor_ai.content.seeder``.

Import from the canonical path instead::

    from ceptor_ai.content.seeder import SimpleSeeder
    from ceptor_ai.content.seeder.providers import PersonProvider
"""
from __future__ import annotations
from ceptor_ai.content.seeder import SimpleSeeder  # noqa: F401
from ceptor_ai.content.seeder.providers import *   # noqa: F401,F403

__all__ = ["SimpleSeeder"]
