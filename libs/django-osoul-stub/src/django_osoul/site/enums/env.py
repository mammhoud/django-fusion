"""Stub environment enums for django-osoul."""


class Environment:
    """Stub Environment enum."""
    pass


class Runtime:
    """Stub Runtime enum."""
    pass


class Module:
    """Stub Module enum."""
    pass


class Direction:
    """Stub Direction enum."""
    pass


def __getattr__(name):
    """Return a stub class for any requested attribute."""
    class FakeAttr:
        pass
    return FakeAttr


__all__ = ["Environment", "Runtime", "Module", "Direction"]
