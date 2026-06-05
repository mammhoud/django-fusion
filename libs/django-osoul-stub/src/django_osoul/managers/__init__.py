"""Stub managers module for django-osoul."""


def __getattr__(name):
    """Return a stub class for any requested attribute."""
    class FakeAttr:
        pass
    return FakeAttr


__all__ = []
