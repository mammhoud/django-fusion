"""Stub upload enums for django-osoul."""


class FileUploadStorage:
    """Stub FileUploadStorage enum."""
    pass


class FileUploadStrategy:
    """Stub FileUploadStrategy enum."""
    pass


def __getattr__(name):
    """Return a stub class for any requested attribute."""
    class FakeAttr:
        pass
    return FakeAttr


__all__ = ["FileUploadStorage", "FileUploadStrategy"]
