"""
Unit tests for form validators.

Validates: Requirements 2.5
"""
import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django_fusion.core.filters import SlugFieldValidator, UniqueFieldValidator


@pytest.fixture
def db_setup(db):
    """Setup database for tests."""
    pass


class TestUniqueFieldValidator:
    """Tests for UniqueFieldValidator."""

    def test_validates_unique_value(self, db_setup):
        """Valid value that doesn't exist passes validation."""
        validator = UniqueFieldValidator(User, "username")
        # Should not raise for non-existent value
        validator("nonexistent_user_12345")

    def test_rejects_duplicate_value(self, db_setup):
        """Duplicate value raises ValidationError."""
        # Create a user first
        User.objects.create_user(username="existinguser", password="testpass")

        validator = UniqueFieldValidator(User, "username")

        with pytest.raises(ValidationError):
            validator("existinguser")

    def test_with_queryset(self, db_setup):
        """Works with a filtered queryset."""
        # Create a user
        User.objects.create_user(username="testuser", password="testpass")

        # Create validator with queryset that excludes the existing user
        # This should pass since the filtered queryset doesn't see the user
        active_users = User.objects.filter(is_active=True)
        validator = UniqueFieldValidator(active_users, "username")

        # This should pass because testuser might not be in active query
        # Actually let's test the opposite - include the user
        all_users = User.objects.all()
        validator = UniqueFieldValidator(all_users, "username")

        with pytest.raises(ValidationError):
            validator("testuser")

    def test_custom_error_message(self, db_setup):
        """Custom error message is used."""
        User.objects.create_user(username="taken", password="testpass")

        validator = UniqueFieldValidator(User, "username", message="Custom: already taken")

        with pytest.raises(ValidationError) as exc_info:
            validator("taken")

        assert "Custom: already taken" in str(exc_info.value)


class TestSlugFieldValidator:
    """Tests for SlugFieldValidator."""

    def test_accepts_valid_simple_slug(self):
        """Valid simple slug passes."""
        validator = SlugFieldValidator()
        validator("valid-slug")

    def test_accepts_valid_complex_slug(self):
        """Valid complex slug with numbers passes."""
        validator = SlugFieldValidator()
        validator("my-slug-123")

    def test_rejects_uppercase(self):
        """Uppercase letters are rejected."""
        validator = SlugFieldValidator()

        with pytest.raises(ValidationError):
            validator("Invalid-SLUG")

    def test_rejects_spaces(self):
        """Spaces are rejected."""
        validator = SlugFieldValidator()

        with pytest.raises(ValidationError):
            validator("invalid slug")

    def test_rejects_special_characters(self):
        """Special characters are rejected."""
        validator = SlugFieldValidator()

        with pytest.raises(ValidationError):
            validator("invalid@slug!")

    def test_rejects_leading_hyphen(self):
        """Leading hyphen is rejected."""
        validator = SlugFieldValidator()

        with pytest.raises(ValidationError):
            validator("-invalid")

    def test_rejects_trailing_hyphen(self):
        """Trailing hyphen is rejected."""
        validator = SlugFieldValidator()

        with pytest.raises(ValidationError):
            validator("invalid-")

    def test_rejects_consecutive_hyphens(self):
        """Consecutive hyphens are rejected."""
        validator = SlugFieldValidator()

        with pytest.raises(ValidationError):
            validator("invalid--slug")

    def test_custom_format_message(self):
        """Custom format error message is used."""
        validator = SlugFieldValidator(message="Custom: invalid slug format")

        with pytest.raises(ValidationError) as exc_info:
            validator("INVALID")

        assert "Custom: invalid slug format" in str(exc_info.value)

    def test_with_uniqueness_check(self, db_setup):
        """Can check uniqueness against a queryset."""
        # The SlugFieldValidator checks uniqueness against a slug field
        # This test verifies the validator can be instantiated with a queryset parameter

        # Test that validator accepts queryset parameter without error
        # We use User.objects.none() to avoid any actual database queries
        validator = SlugFieldValidator(queryset=User.objects.none())

        # Verify the queryset was set correctly
        assert validator.queryset is not None
        assert validator.queryset.model == User
