"""
craftsai.seeder.providers
==========================

Extended Faker provider with extra data types not covered by the default
Faker package.

No Django dependency.

Classes
-------
FakerProvider
    Adds ``duration``, ``uuid``, ``rand_small_int``, ``rand_big_int``,
    ``rand_float``, ``file_name``, ``comma_sep_ints``, and ``binary``
    generators.
"""

from __future__ import annotations

import random
import sys
import time
import uuid
from datetime import timedelta


class FakerProvider:
    """
    Extra data providers for use with :class:`craftsai.seeder.SimpleSeeder`.

    Args:
        faker: A :class:`faker.Faker` instance.

    Usage::

        from faker import Faker
        from craftsai.seeder.providers import FakerProvider

        faker = Faker()
        provider = FakerProvider(faker)
        print(provider.uuid())          # UUID4 object
        print(provider.rand_big_int())  # large random integer
    """

    _FILE_EXTENSIONS = (
        "flac", "mp3", "wav", "bmp", "gif", "jpeg", "jpg", "png",
        "tiff", "css", "csv", "html", "js", "json", "txt", "mp4",
        "avi", "mov", "webm",
    )

    def __init__(self, faker):
        self.faker = faker

    def duration(self) -> timedelta:
        """Return a random :class:`~datetime.timedelta` up to ~34 years."""
        return timedelta(seconds=random.randint(0, int(time.time())))

    def uuid(self) -> uuid.UUID:
        """Return a random UUID4."""
        return uuid.uuid4()

    def rand_small_int(self, pos: bool = False) -> int:
        """
        Return a random small integer.

        Args:
            pos: If ``True`` return a non-negative value (0–32767).

        Returns:
            int in range [-32768, 32767] or [0, 32767].
        """
        return random.randint(0, 32767) if pos else random.randint(-32768, 32767)

    def rand_int(self, pos: bool = False) -> int:
        """Return a random 32-bit integer."""
        return random.randint(0, 4_294_967_295) if pos else random.randint(-4_294_967_295, 4_294_967_295)

    def rand_big_int(self) -> int:
        """Return a random integer in the full ``sys.maxsize`` range."""
        return random.randint(-sys.maxsize, sys.maxsize)

    def rand_float(self) -> float:
        """Return a random float in [0.0, 1.0)."""
        return random.random()

    def file_name(self) -> str:
        """Return a random filename with a common extension."""
        name = self.faker.word()
        ext = random.choice(self._FILE_EXTENSIONS)
        return f"{name}.{ext}"

    def comma_sep_ints(self) -> str:
        """Return a comma-separated string of 10 random integers."""
        return ",".join(str(self.rand_int()) for _ in range(10))

    def binary(self) -> bytes:
        """Return random binary data (up to 512 bytes)."""
        return str.encode(str(self.faker.text(512)))
