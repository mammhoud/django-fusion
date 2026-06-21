"""
craftsai.seeder.simple_seeder
==============================

Framework-agnostic data seeder built on top of Faker.

No Django, no ORM — just plain Python dicts.

Classes
-------
SimpleSeeder
    Generates lists of fake-data dictionaries from a schema definition.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Union

logger = logging.getLogger(__name__)

# Schema value can be a Faker attribute name (str) or a callable that
# receives the Faker instance and returns a value.
SchemaValue = Union[str, Callable]


class SimpleSeeder:
    """
    Generate fake data records from a schema without any ORM dependency.

    Args:
        faker: A :class:`faker.Faker` instance.  If ``None`` a default
            English instance is created automatically.

    Usage::

        from faker import Faker
        from craftsai.seeder import SimpleSeeder

        seeder = SimpleSeeder(Faker())

        records = seeder.generate(count=5, schema={
            "name":  "name",
            "email": "email",
            "score": lambda f: f.random_int(0, 100),
        })
        # records → [{"name": "...", "email": "...", "score": 42}, ...]
    """

    def __init__(self, faker=None):
        if faker is None:
            try:
                from faker import Faker
                faker = Faker()
            except ImportError as exc:
                raise ImportError(
                    "Faker is required for craftsai.seeder. "
                    "Install it with: pip install faker"
                ) from exc
        self.faker = faker

    def generate(self, count: int, schema: Dict[str, SchemaValue]) -> List[Dict[str, Any]]:
        """
        Generate *count* fake-data records according to *schema*.

        Args:
            count: Number of records to generate.
            schema: Mapping of field name → Faker attribute name (str) or
                callable ``(faker) → value``.

        Returns:
            List of dicts, one per record.

        Raises:
            ValueError: If *count* is not a positive integer.

        Example::

            records = seeder.generate(3, {"title": "sentence", "body": "text"})
        """
        if count < 1:
            raise ValueError(f"count must be >= 1, got {count}")

        results = []
        for _ in range(count):
            record: Dict[str, Any] = {}
            for field, spec in schema.items():
                try:
                    if callable(spec):
                        record[field] = spec(self.faker)
                    else:
                        record[field] = getattr(self.faker, spec)()
                except Exception as exc:
                    logger.warning("Failed to generate field '%s': %s", field, exc)
                    record[field] = None
            results.append(record)
        return results

    def generate_one(self, schema: Dict[str, SchemaValue]) -> Dict[str, Any]:
        """
        Generate a single fake-data record.

        Args:
            schema: Same format as :meth:`generate`.

        Returns:
            A single dict.
        """
        return self.generate(1, schema)[0]
