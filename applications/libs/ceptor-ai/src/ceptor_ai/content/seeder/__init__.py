"""Content seeder — deterministic database population for development and testing.

Provides Faker-backed providers and a simple seed runner that creates
consistent fixture data across sites without requiring JSON fixture files.

Usage::

    from ceptor_ai.content.seeder import SimpleSeeder
    from ceptor_ai.content.seeder.providers import PersonProvider
"""

from .simple_seeder import SimpleSeeder

__all__ = ["SimpleSeeder"]
