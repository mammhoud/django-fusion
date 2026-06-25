"""
Minimal integration test for django-rseal email features.

This test verifies basic integration without triggering all the model issues.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings before importing django-rseal
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

import django

django.setup()

import pytest


def test_crafts_ai_import():
    """Test that django-rseal modules can be imported."""
    # Test importing key modules
    try:
        from crafts_ai.email.services import BulkEmailService, EmailService
        from crafts_ai.email.templates.template_selector import RoleBasedEmailTemplateSelector

        # Verify modules can be imported
        assert RoleBasedEmailTemplateSelector is not None
        assert EmailService is not None
        assert BulkEmailService is not None

        print("✓ django-rseal modules imported successfully")

    except ImportError as e:
        pytest.fail(f"Failed to import django-rseal modules: {e}")


def test_template_selector_basic():
    """Test basic template selector functionality."""
    from crafts_ai.email.templates.template_selector import RoleBasedEmailTemplateSelector

    # Create selector
    selector = RoleBasedEmailTemplateSelector(
        site_name="Test Site",
        site_url="https://test.example.com",
        support_email="support@test.example.com",
    )

    # Test basic methods
    assert selector.site_name == "Test Site"
    assert selector.site_url == "https://test.example.com"
    assert selector.support_email == "support@test.example.com"

    # Test template path resolution
    admin_path = selector.get_template_path("admin")
    assert admin_path == "components/email/admin/base.html"

    user_path = selector.get_template_path("user")
    assert user_path == "components/email/user/base.html"

    default_path = selector.get_template_path("unknown")
    assert default_path == "components/email/base.html"

    print("✓ Template selector basic functionality works")


def test_email_service_basic():
    """Test basic email service functionality."""
    from crafts_ai.email.services import EmailService

    # Create service
    service = EmailService()

    # Test basic properties
    assert service.from_email == "noreply@example.com"  # From test settings

    print("✓ Email service basic functionality works")


def test_build_context():
    """Test context building."""
    from crafts_ai.email.templates.template_selector import RoleBasedEmailTemplateSelector

    selector = RoleBasedEmailTemplateSelector(
        site_name="Test Site",
        site_url="https://test.example.com",
        support_email="support@test.example.com",
    )

    # Build context
    context = selector.build_context(
        email="user@example.com",
        role="user",
        custom_data="test",
    )

    # Verify context
    assert context["email"] == "user@example.com"
    assert context["role"] == "user"
    assert context["site_name"] == "Test Site"
    assert context["site_url"] == "https://test.example.com"
    assert context["support_email"] == "support@test.example.com"
    assert context["custom_data"] == "test"

    print("✓ Context building works")


if __name__ == "__main__":
    # Run tests
    test_crafts_ai_import()
    test_template_selector_basic()
    test_email_service_basic()
    test_build_context()
    print("\n✅ All minimal integration tests passed!")
