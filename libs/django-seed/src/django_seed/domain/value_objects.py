"""
Value Objects for Django Seed package.

Value objects are immutable objects that represent descriptive aspects of the domain
with no conceptual identity. They are defined by their attributes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, ClassVar, Optional, Self
from uuid import UUID, uuid4

from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email


@dataclass(frozen=True, slots=True, kw_only=True)
class ValueObject:
    """Base class for all value objects."""

    def __post_init__(self) -> None:
        """Validate the value object after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the value object.

        Subclasses should override this method to implement validation logic.
        """
        pass

    def __eq__(self, other: Any) -> bool:
        """Two value objects are equal if they have the same type and attributes."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """Hash based on the value object's attributes."""
        return hash(tuple(sorted(self.__dict__.items())))


@dataclass(frozen=True, slots=True)
class Email(ValueObject):
    """Email value object with validation."""

    value: str

    def validate(self) -> None:
        """Validate email format."""
        try:
            django_validate_email(self.value)
        except ValidationError as e:
            raise ValueError(f"Invalid email address: {self.value}") from e

    @property
    def domain(self) -> str:
        """Get the domain part of the email."""
        return self.value.split('@')[1]

    @property
    def local_part(self) -> str:
        """Get the local part of the email."""
        return self.value.split('@')[0]


@dataclass(frozen=True, slots=True)
class Money(ValueObject):
    """Money value object with currency support."""

    amount: Decimal
    currency: str = "USD"

    def validate(self) -> None:
        """Validate money amount and currency."""
        if self.amount < Decimal('0'):
            raise ValueError("Money amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency code must be 3 characters")

    def __add__(self, other: Self) -> Self:
        """Add two money objects with the same currency."""
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Self) -> Self:
        """Subtract two money objects with the same currency."""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: Decimal) -> Self:
        """Multiply money by a decimal multiplier."""
        return Money(self.amount * multiplier, self.currency)

    def __truediv__(self, divisor: Decimal) -> Self:
        """Divide money by a decimal divisor."""
        if divisor == Decimal('0'):
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / divisor, self.currency)


@dataclass(frozen=True, slots=True)
class Percentage(ValueObject):
    """Percentage value object."""

    value: Decimal

    def validate(self) -> None:
        """Validate percentage value."""
        if not Decimal('0') <= self.value <= Decimal('100'):
            raise ValueError("Percentage must be between 0 and 100")

    @property
    def decimal(self) -> Decimal:
        """Get the percentage as a decimal (e.g., 50% -> 0.5)."""
        return self.value / Decimal('100')

    @classmethod
    def from_decimal(cls, decimal_value: Decimal) -> Self:
        """Create a percentage from a decimal value."""
        return cls(decimal_value * Decimal('100'))


@dataclass(frozen=True, slots=True)
class Duration(ValueObject):
    """Duration value object."""

    seconds: int

    def validate(self) -> None:
        """Validate duration."""
        if self.seconds < 0:
            raise ValueError("Duration cannot be negative")

    @property
    def minutes(self) -> float:
        """Get duration in minutes."""
        return self.seconds / 60

    @property
    def hours(self) -> float:
        """Get duration in hours."""
        return self.seconds / 3600

    @property
    def days(self) -> float:
        """Get duration in days."""
        return self.seconds / 86400

    @classmethod
    def from_minutes(cls, minutes: float) -> Self:
        """Create duration from minutes."""
        return cls(int(minutes * 60))

    @classmethod
    def from_hours(cls, hours: float) -> Self:
        """Create duration from hours."""
        return cls(int(hours * 3600))

    @classmethod
    def from_days(cls, days: float) -> Self:
        """Create duration from days."""
        return cls(int(days * 86400))

    def __add__(self, other: Self) -> Self:
        """Add two durations."""
        return Duration(self.seconds + other.seconds)

    def __sub__(self, other: Self) -> Self:
        """Subtract two durations."""
        return Duration(self.seconds - other.seconds)


@dataclass(frozen=True, slots=True)
class ObjectType(ValueObject):
    """Object type value object for type-safe object definitions."""

    name: str
    version: str = "1.0.0"
    schema: Optional[dict] = None
    metadata: dict = field(default_factory=dict)

    def validate(self) -> None:
        """Validate object type."""
        if not self.name:
            raise ValueError("Object type name cannot be empty")
        if not self.version:
            raise ValueError("Object type version cannot be empty")

    @property
    def full_name(self) -> str:
        """Get the full name including version."""
        return f"{self.name}@{self.version}"

    def is_compatible_with(self, other: Self) -> bool:
        """Check if this object type is compatible with another."""
        if self.name != other.name:
            return False

        # Simple version compatibility check
        # This could be enhanced with semantic versioning
        return self.version == other.version


@dataclass(frozen=True, slots=True)
class CacheKey(ValueObject):
    """Cache key value object."""

    prefix: str
    key: str
    version: int = 1

    def validate(self) -> None:
        """Validate cache key."""
        if not self.prefix:
            raise ValueError("Cache key prefix cannot be empty")
        if not self.key:
            raise ValueError("Cache key cannot be empty")
        if self.version < 1:
            raise ValueError("Cache key version must be positive")

    @property
    def full_key(self) -> str:
        """Get the full cache key."""
        return f"{self.prefix}:{self.version}:{self.key}"

    @classmethod
    def from_string(cls, key_string: str) -> Self:
        """Create a cache key from a string."""
        parts = key_string.split(':')
        if len(parts) != 3:
            raise ValueError(f"Invalid cache key format: {key_string}")

        prefix, version_str, key = parts
        try:
            version = int(version_str)
        except ValueError:
            raise ValueError(f"Invalid version in cache key: {version_str}")

        return cls(prefix=prefix, key=key, version=version)
