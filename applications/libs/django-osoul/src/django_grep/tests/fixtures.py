"""Test fixtures and factory helpers."""
from django.contrib.auth import get_user_model

User = get_user_model()


def create_test_user(username="testuser", email="test@example.com", password="testpass123", **kwargs):
    """Create a standard test user."""
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        **kwargs,
    )


def create_superuser(username="admin", email="admin@example.com", password="adminpass123", **kwargs):
    """Create a superuser for admin tests."""
    return User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        **kwargs,
    )


class UserFactory:
    """Simple user factory for tests."""

    _counter = 0

    @classmethod
    def create(cls, **kwargs):
        """Create a unique test user."""
        cls._counter += 1
        defaults = {
            "username": f"user_{cls._counter}",
            "email": f"user_{cls._counter}@example.com",
            "password": "testpass123",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    @classmethod
    def create_batch(cls, count: int, **kwargs):
        """Create multiple test users."""
        return [cls.create(**kwargs) for _ in range(count)]

    @classmethod
    def reset(cls):
        """Reset the counter (call in tearDown if needed)."""
        cls._counter = 0
