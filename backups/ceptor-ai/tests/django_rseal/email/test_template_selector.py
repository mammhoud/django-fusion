"""
Tests for django-rseal RoleBasedEmailTemplateSelector.

These tests verify role-based template selection, context building, and rendering.
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Add the project root to Python path so tests.settings can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from django.test.utils import override_settings

# Configure Django settings before importing django-rseal
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

import django

django.setup()

from ceptor_ai.email.templates.template_selector import RoleBasedEmailTemplateSelector


@pytest.mark.django_db
class TestRoleBasedEmailTemplateSelector:
    """Test RoleBasedEmailTemplateSelector functionality."""

    @pytest.fixture
    def selector(self):
        """Fixture providing template selector instance."""
        return RoleBasedEmailTemplateSelector(
            site_name="Test Site",
            site_url="https://test.example.com",
            support_email="support@test.example.com",
        )

    def test_selector_initialization(self):
        """Test template selector initialization."""
        # Test with custom values
        selector = RoleBasedEmailTemplateSelector(
            site_name="Custom Site",
            site_url="https://custom.example.com",
            support_email="help@custom.example.com",
        )

        assert selector.site_name == "Custom Site"
        assert selector.site_url == "https://custom.example.com"
        assert selector.support_email == "help@custom.example.com"

        # Test with defaults from settings
        with override_settings(
            WAGTAIL_SITE_NAME="Settings Site",
            WAGTAILADMIN_BASE_URL="https://settings.example.com",
            DEFAULT_FROM_EMAIL="noreply@settings.example.com",
        ):
            selector2 = RoleBasedEmailTemplateSelector()

            assert selector2.site_name == "Settings Site"
            assert selector2.site_url == "https://settings.example.com"
            assert selector2.support_email == "noreply@settings.example.com"

    def test_get_template_path(self, selector):
        """Test template path resolution."""
        # Test role-specific templates
        assert selector.get_template_path("admin") == "components/email/admin/base.html"
        assert selector.get_template_path("supervisor") == "components/email/supervisor/base.html"
        assert selector.get_template_path("user") == "components/email/user/base.html"

        # Test default for unknown role
        assert selector.get_template_path("unknown") == "components/email/base.html"
        assert selector.get_template_path("") == "components/email/base.html"
        assert selector.get_template_path(None) == "components/email/base.html"

        # Test with legacy templates
        assert selector.get_template_path("admin", use_legacy=True) == "components/email/legacy/admin/base.html"
        assert selector.get_template_path("unknown", use_legacy=True) == "components/email/legacy/base.html"

    def test_get_role_context(self, selector):
        """Test role context building."""
        # Test admin role context
        admin_context = selector.get_role_context("admin")
        assert admin_context["role_display"] == "Administrator"
        assert admin_context["role_color"] == "#4CAF50"
        assert "Full system access" in admin_context["permissions"]
        assert len(admin_context["permissions"]) == 6

        # Test supervisor role context
        supervisor_context = selector.get_role_context("supervisor")
        assert supervisor_context["role_display"] == "Supervisor"
        assert supervisor_context["role_color"] == "#2196F3"
        assert "Team management" in supervisor_context["permissions"]
        assert len(supervisor_context["permissions"]) == 6

        # Test user role context
        user_context = selector.get_role_context("user")
        assert user_context["role_display"] == "User"
        assert user_context["role_color"] == "#ff9800"
        assert "Access to resources" in user_context["permissions"]
        assert len(user_context["permissions"]) == 5

        # Test unknown role context (default)
        unknown_context = selector.get_role_context("unknown")
        assert unknown_context["role_display"] == "Unknown"
        assert unknown_context["role_color"] == "#666"
        assert unknown_context["permissions"] == []

    def test_build_context(self, selector):
        """Test complete context building."""
        # Build context for admin role
        context = selector.build_context(
            email="admin@example.com",
            role="admin",
            custom_key="custom_value",
            another_key="another_value",
        )

        # Check required fields
        assert context["email"] == "admin@example.com"
        assert context["role"] == "admin"
        assert context["site_name"] == "Test Site"
        assert context["site_url"] == "https://test.example.com"
        assert context["support_email"] == "support@test.example.com"

        # Check role-specific fields
        assert context["role_display"] == "Administrator"
        assert context["role_color"] == "#4CAF50"
        assert "permissions" in context
        assert len(context["permissions"]) > 0

        # Check custom fields
        assert context["custom_key"] == "custom_value"
        assert context["another_key"] == "another_value"

        # Build context for user role
        user_context = selector.build_context(
            email="user@example.com",
            role="user",
            user_name="Test User",
        )

        assert user_context["email"] == "user@example.com"
        assert user_context["role"] == "user"
        assert user_context["role_display"] == "User"
        assert user_context["role_color"] == "#ff9800"
        assert user_context["user_name"] == "Test User"

    @patch('ceptor_ai.email.templates.template_selector.render_to_string')
    def test_render_email_success(self, mock_render, selector):
        """Test successful email rendering."""
        # Mock template rendering
        mock_render.return_value = "<h1>Admin Email</h1><p>Test content</p>"

        context = {
            "email": "admin@example.com",
            "role": "admin",
            "site_name": "Test Site",
        }

        html, text = selector.render_email("admin", context)

        # Verify rendering was called
        mock_render.assert_called_once_with(
            "components/email/admin/base.html",
            context,
        )

        # Verify results
        assert html == "<h1>Admin Email</h1><p>Test content</p>"
        assert text == "Admin EmailTest content"  # Stripped HTML

    @patch('ceptor_ai.email.templates.template_selector.render_to_string')
    def test_render_email_fallback(self, mock_render, selector):
        """Test email rendering with fallback."""
        # Mock first render to fail
        mock_render.side_effect = [
            Exception("Template not found"),  # First call fails
            "<h1>Default Email</h1><p>Fallback content</p>",  # Fallback succeeds
        ]

        context = {
            "email": "unknown@example.com",
            "role": "unknown",
        }

        html, text = selector.render_email("unknown", context)

        # Verify fallback was used
        assert mock_render.call_count == 2

        # First call: role-specific template
        mock_render.assert_any_call(
            "components/email/base.html",  # Default for unknown role
            context,
        )

        # Second call: default template
        mock_render.assert_any_call(
            "components/email/base.html",  # Default template
            context,
        )

        # Verify fallback results
        assert html == "<h1>Default Email</h1><p>Fallback content</p>"
        assert text == "Default EmailFallback content"

    @patch('ceptor_ai.email.templates.template_selector.render_to_string')
    def test_render_email_legacy(self, mock_render, selector):
        """Test email rendering with legacy templates."""
        mock_render.return_value = "<h1>Legacy Email</h1><p>Legacy content</p>"

        context = {
            "email": "user@example.com",
            "role": "user",
        }

        html, text = selector.render_email("user", context, use_legacy=True)

        # Verify legacy template was used
        mock_render.assert_called_once_with(
            "components/email/legacy/base.html",  # Legacy default template
            context,
        )

        assert html == "<h1>Legacy Email</h1><p>Legacy content</p>"
        assert text == "Legacy EmailLegacy content"

    @patch('ceptor_ai.email.templates.template_selector.render_to_string')
    def test_render_email_complete_flow(self, mock_render, selector):
        """Test complete email rendering flow."""
        mock_render.return_value = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Template</title>
            <style>
                body { font-family: Arial; }
                .role-badge { background: #2196F3; }
            </style>
        </head>
        <body>
            <h1>Hello Supervisor!</h1>
            <div class="role-badge">supervisor</div>
            <p>Welcome to Test Site</p>
        </body>
        </html>
        """

        # Build complete context
        context = selector.build_context(
            email="supervisor@example.com",
            role="supervisor",
            team_name="Development Team",
            report_period="Q2 2026",
        )

        # Render email
        html, text = selector.render_email("supervisor", context)

        # Verify template was rendered with supervisor context
        mock_render.assert_called_once_with(
            "components/email/supervisor/base.html",
            context,
        )

        # Verify HTML contains expected content
        assert "Hello Supervisor!" in html
        assert "Welcome to Test Site" in html
        assert "supervisor" in html

        # Verify text version
        assert "Hello Supervisor!" in text
        assert "Welcome to Test Site" in text

    def test_selector_customization(self):
        """Test template selector customization via subclassing."""
        class CustomTemplateSelector(RoleBasedEmailTemplateSelector):
            """Custom template selector with modified templates."""

            ROLE_TEMPLATES = {
                "admin": "custom/email/admin.html",
                "supervisor": "custom/email/supervisor.html",
                "user": "custom/email/user.html",
                "default": "custom/email/default.html",
            }

            LEGACY_TEMPLATES = {
                "admin": "custom/email/legacy/admin.html",
                "default": "custom/email/legacy/default.html",
            }

            def get_role_context(self, role: str):
                """Custom role context."""
                if role == "custom":
                    return {
                        "role_display": "Custom Role",
                        "role_color": "#FF5733",
                        "permissions": ["Custom permission 1", "Custom permission 2"],
                    }
                return super().get_role_context(role)

        # Test custom selector
        custom_selector = CustomTemplateSelector(
            site_name="Custom Site",
            site_url="https://custom.example.com",
        )

        # Verify custom templates
        assert custom_selector.get_template_path("admin") == "custom/email/admin.html"
        assert custom_selector.get_template_path("supervisor") == "custom/email/supervisor.html"
        assert custom_selector.get_template_path("user") == "custom/email/user.html"
        assert custom_selector.get_template_path("unknown") == "custom/email/default.html"

        # Verify custom legacy templates
        assert custom_selector.get_template_path("admin", use_legacy=True) == "custom/email/legacy/admin.html"
        assert custom_selector.get_template_path("unknown", use_legacy=True) == "custom/email/legacy/default.html"

        # Verify custom role context
        custom_context = custom_selector.get_role_context("custom")
        assert custom_context["role_display"] == "Custom Role"
        assert custom_context["role_color"] == "#FF5733"
        assert "Custom permission 1" in custom_context["permissions"]

        # Verify inherited role context still works
        admin_context = custom_selector.get_role_context("admin")
        assert admin_context["role_display"] == "Administrator"
        assert admin_context["role_color"] == "#4CAF50"

    def test_selector_integration_with_email_service(self, selector):
        """Test selector integration with email service workflow."""
        # Build context for email
        context = selector.build_context(
            email="recipient@example.com",
            role="admin",
            action="Password Reset",
            reset_url="https://example.com/reset/123",
            expiry_hours=24,
        )

        # Verify context contains all necessary fields
        assert context["email"] == "recipient@example.com"
        assert context["role"] == "admin"
        assert context["site_name"] == "Test Site"
        assert context["site_url"] == "https://test.example.com"
        assert context["support_email"] == "support@test.example.com"
        assert context["action"] == "Password Reset"
        assert context["reset_url"] == "https://example.com/reset/123"
        assert context["expiry_hours"] == 24

        # Verify role-specific fields
        assert context["role_display"] == "Administrator"
        assert context["role_color"] == "#4CAF50"
        assert "permissions" in context

        # Get template path for this role
        template_path = selector.get_template_path("admin")
        assert template_path == "components/email/admin/base.html"

        # This context and template path can now be used with EmailService
        # Example:
        # from ceptor_ai.email.services import EmailService
        # service = EmailService()
        # service.send_email(
        #     recipient=context["email"],
        #     subject=f"{context['action']} - {context['site_name']}",
        #     template_name=template_path,
        #     context=context,
        #     queue=True,
        # )

    @patch('ceptor_ai.email.templates.template_selector.render_to_string')
    def test_performance_with_multiple_renders(self, mock_render, selector):
        """Test selector performance with multiple renders."""
        import time

        mock_render.return_value = "<h1>Test Email</h1><p>Performance test</p>"

        # Build context once
        context = selector.build_context(
            email="test@example.com",
            role="user",
            test_data="performance",
        )

        # Time multiple renders
        start_time = time.time()

        results = []
        for i in range(50):  # Render 50 emails
            html, text = selector.render_email("user", context)
            results.append((html, text))

        end_time = time.time()
        duration = end_time - start_time

        # Verify all renders succeeded
        assert len(results) == 50
        for html, text in results:
            assert html == "<h1>Test Email</h1><p>Performance test</p>"
            assert text == "Test EmailPerformance test"

        # Performance check: 50 renders should be fast
        # This is a sanity check, not a strict performance requirement
        assert duration < 2.0, f"50 renders took {duration:.2f} seconds"

    def test_error_handling_edge_cases(self, selector):
        """Test error handling for edge cases."""
        # Test with empty role
        context1 = selector.build_context(
            email="test@example.com",
            role="",
            test="empty role",
        )
        assert context1["role"] == ""
        assert context1["role_display"] == ""  # Empty string capitalized

        # Test with None role - returns "User" as safe default
        context2 = selector.build_context(
            email="test@example.com",
            role=None,
            test="none role",
        )
        assert context2["role"] is None
        assert context2["role_display"] == "User"  # Safe default for None role

        # Test with very long role name
        long_role = "a" * 100
        context3 = selector.build_context(
            email="test@example.com",
            role=long_role,
            test="long role",
        )
        assert context3["role"] == long_role
        assert context3["role_display"] == long_role.capitalize()

        # Test with special characters in role
        special_role = "admin-super_user.test@role"
        context4 = selector.build_context(
            email="test@example.com",
            role=special_role,
            test="special role",
        )
        assert context4["role"] == special_role
        assert context4["role_display"] == "Admin-super_user.test@role"  # Capitalized
