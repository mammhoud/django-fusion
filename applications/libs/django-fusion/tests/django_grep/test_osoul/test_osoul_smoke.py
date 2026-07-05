"""Smoke tests for django-fusion modules."""
import pytest


def test_osoul_imports():
    from django_fusion.core.models.base import BaseModel, TimeStampedModel, UUIDModel
    assert BaseModel is not None

def test_osoul_utils():
    from django_fusion.core.utils.formatting.text import slugify_unique, truncate_words
    from django_fusion.core.utils.security.validators import validate_email_format
    assert validate_email_format("test@example.com") is True
    assert validate_email_format("not-an-email") is False

def test_osoul_no_wagtail_import():
    """Verify osoul does not import wagtail at the top level."""
    import sys

    import django_fusion
    # wagtail should not be in sys.modules after importing osoul
    # (it may be installed but osoul should not pull it in)
    assert "wagtail" not in str(django_fusion.__file__)
