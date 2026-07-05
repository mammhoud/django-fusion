"""Tests for Django Osoul utilities."""

from datetime import datetime, timedelta

import pytest
from django.utils import timezone
from django_fusion.core.utils.formatting.text import (
    capitalize_words,
    slugify_unique,
    strip_html_tags,
    truncate_chars,
    truncate_words,
)
from django_fusion.core.utils.data.datetime_utils import (
    format_date_range,
    format_duration,
    format_relative_time,
    get_time_until,
    is_business_day,
)


class TestTextUtils:
    """Test text utility functions."""

    def test_truncate_words(self):
        """Test word truncation."""
        text = "This is a very long text that needs to be truncated"
        result = truncate_words(text, 5)
        assert result == "This is a very long..."

    def test_truncate_words_no_truncation(self):
        """Test word truncation when not needed."""
        text = "Short text"
        result = truncate_words(text, 5)
        assert result == "Short text"

    def test_truncate_chars(self):
        """Test character truncation."""
        text = "This is a very long text"
        result = truncate_chars(text, 10)
        assert "This is a" in result and "..." in result

    def test_truncate_chars_no_truncation(self):
        """Test character truncation when not needed."""
        text = "Short"
        result = truncate_chars(text, 10)
        assert result == "Short"

    def test_strip_html_tags(self):
        """Test HTML tag stripping."""
        html = "<p>Hello <strong>World</strong></p>"
        result = strip_html_tags(html)
        assert result == "Hello World"

    def test_capitalize_words(self):
        """Test word capitalization."""
        text = "hello world"
        result = capitalize_words(text)
        assert result == "Hello World"


class TestDateTimeUtils:
    """Test datetime utility functions."""

    def test_format_relative_time_just_now(self):
        """Test relative time formatting for recent times."""
        dt = timezone.now() - timedelta(seconds=30)
        result = format_relative_time(dt)
        assert result == "just now"

    def test_format_relative_time_minutes_ago(self):
        """Test relative time formatting for minutes ago."""
        dt = timezone.now() - timedelta(minutes=5)
        result = format_relative_time(dt)
        assert "minute" in result

    def test_format_duration(self):
        """Test duration formatting."""
        result = format_duration(3661)
        assert result  # non-empty result
        assert "1" in result  # contains the hour/minute/second count

    def test_format_date_range_same_month(self):
        """Test date range formatting for same month."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)
        result = format_date_range(start, end)
        assert "Jan" in result or "January" in result

    def test_is_business_day_monday(self):
        """Test business day check for Monday."""
        # 2024-01-01 is a Monday
        date = datetime(2024, 1, 1)
        assert is_business_day(date) is True

    def test_is_business_day_saturday(self):
        """Test business day check for Saturday."""
        # 2024-01-06 is a Saturday
        date = datetime(2024, 1, 6)
        assert is_business_day(date) is False


class TestValidators:
    """Test validator functions."""

    def test_validate_email_format_valid(self):
        """Test valid email format."""
        from django_fusion.core.utils.security.validators import validate_email_format
        assert validate_email_format("user@example.com") is True

    def test_validate_email_format_invalid(self):
        """Test invalid email format."""
        from django_fusion.core.utils.security.validators import validate_email_format
        assert validate_email_format("invalid-email") is False

    def test_validate_phone_number_valid(self):
        """Test valid phone number."""
        from django_fusion.core.utils.security.validators import validate_phone_number
        assert validate_phone_number("+1-555-123-4567") is True

    def test_validate_phone_number_invalid(self):
        """Test invalid phone number."""
        from django_fusion.core.utils.security.validators import validate_phone_number
        assert validate_phone_number("invalid") is False

    def test_validate_url_valid(self):
        """Test valid URL."""
        from django_fusion.core.utils.security.validators import validate_url
        assert validate_url("https://example.com") is True

    def test_validate_url_invalid(self):
        """Test invalid URL."""
        from django_fusion.core.utils.security.validators import validate_url
        assert validate_url("not-a-url") is False

    def test_validate_username_valid(self):
        """Test valid username."""
        from django_fusion.core.utils.security.validators import validate_username
        assert validate_username("john_doe") is True

    def test_validate_username_too_short(self):
        """Test username too short."""
        from django_fusion.core.utils.security.validators import validate_username
        assert validate_username("ab") is False
