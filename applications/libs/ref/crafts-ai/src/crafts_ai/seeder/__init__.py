"""
craftsai.seeder
===============

Faker-based data generation utilities — **no Django required**.

For seeding Django models use ``django_rseal.seeder`` which wraps these
utilities with Django ORM support.

Classes
-------
SimpleSeeder
    Framework-agnostic seeder that generates fake data dicts via Faker.
FakerProvider
    Extended Faker provider with extra data types (UUID, duration, binary).

Usage::

    from faker import Faker
    from craftsai.seeder import SimpleSeeder

    seeder = SimpleSeeder(Faker())
    records = seeder.generate(count=10, schema={
        "name": "name",
        "email": "email",
        "age": lambda f: f.random_int(18, 80),
    })
"""

from .providers import FakerProvider
from .simple_seeder import SimpleSeeder

__all__ = ["SimpleSeeder", "FakerProvider"]
