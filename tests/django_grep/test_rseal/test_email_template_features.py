"""
Tests for EmailTemplate merge - verifying both import paths work identically.
"""

from datetime import timedelta

import pytest
from django.utils import timezone


def test_canonical_import_paths_work():
    """Canonical import paths should reference the same class."""
    from ceptor_ai.communication.email.models import EmailTemplate as EmailTemplate1
    from ceptor_ai.communication.email.models.models import EmailTemplate as EmailTemplate2

    # Both must resolve to the same EmailTemplate class
    assert EmailTemplate1.__name__ == EmailTemplate2.__name__
    assert EmailTemplate1._meta.app_label == 'ceptor_ai'


def test_simple_usage_backward_compatible():
    """Simple usage pattern should work (backward compatibility)."""
    from ceptor_ai.communication.email.models import EmailTemplate

    template = EmailTemplate.objects.create(
        name="test_simple_usage",
        subject_template="Test Subject",
        html_content="<p>Test content</p>",
        text_content="Test content",
    )

    assert template.name == "test_simple_usage"
    assert template.subject_template == "Test Subject"
    assert template.html_content == "<p>Test content</p>"
    assert template.is_active  # Default value
    assert template.template_type == "newsletter"  # Default value

    # Cleanup
    template.delete()


def test_advanced_features_available():
    """Advanced features should be available through simple import."""
    from ceptor_ai.communication.email.models import EmailTemplate

    future = timezone.now() + timedelta(days=1)

    template = EmailTemplate.objects.create(
        name="test_advanced_features",
        subject_template="Test {{ variable }}",
        html_content="<p>Test {{ variable }}</p>",
        template_type="invitation",
        language="en",
        go_live_at=future,
        is_default=True,
        category="test",
    )

    # Verify advanced fields work
    assert template.template_type == "invitation"
    assert template.language == "en"
    assert template.go_live_at == future
    assert template.is_default
    assert template.category == "test"

    # Verify advanced properties work
    assert not template.is_live  # Not live yet (scheduled for future)
    assert "Scheduled" in template.scheduled_status

    # Cleanup
    template.delete()


def test_advanced_rendering_works():
    """Advanced rendering methods should work."""
    from ceptor_ai.communication.email.models import EmailTemplate

    template = EmailTemplate.objects.create(
        name="test_rendering",
        subject_template="Hello {{ user_name }}",
        html_content="<p>Welcome {{ user_name }} to {{ site_name }}</p>",
        text_content="Welcome {{ user_name }} to {{ site_name }}",
        template_type="welcome",
    )

    # Test rendering with context
    rendered = template.render_for_email({
        "user_name": "John Doe",
        "site_name": "Test Site",
    })

    assert "Hello John Doe" in rendered['subject']
    assert "Welcome John Doe" in rendered['html']
    assert "Test Site" in rendered['html']

    # Cleanup
    template.delete()


def test_class_methods_available():
    """Class methods should be available."""
    from ceptor_ai.communication.email.models import EmailTemplate

    # Create a default template
    template = EmailTemplate.objects.create(
        name="test_class_methods",
        subject_template="Test",
        html_content="<p>Test</p>",
        template_type="notification",
        language="en",
        is_default=True,
        is_active=True,
    )

    # Test get_default_for_type
    found = EmailTemplate.get_default_for_type("notification", "en")
    assert found is not None
    assert found.name == "test_class_methods"

    # Test get_live_templates
    live_templates = EmailTemplate.get_live_templates(template_type="notification")
    assert template in live_templates

    # Cleanup
    template.delete()


def test_scheduling_methods_work():
    """Scheduling methods should work."""
    from ceptor_ai.communication.email.models import EmailTemplate

    template = EmailTemplate.objects.create(
        name="test_scheduling",
        subject_template="Test",
        html_content="<p>Test</p>",
    )

    # Test schedule_for
    future = timezone.now() + timedelta(days=1)
    template.schedule_for(go_live_at=future)
    assert template.go_live_at == future
    assert not template.is_live

    # Test activate_immediately
    template.activate_immediately()
    assert template.go_live_at is None
    assert template.is_active
    assert template.is_live

    # Cleanup
    template.delete()


def test_file_upload_methods_available():
    """File upload methods should be available."""
    from ceptor_ai.communication.email.models import EmailTemplate

    template = EmailTemplate.objects.create(
        name="test_file_methods",
        subject_template="Test",
        html_content="<p>Original content</p>",
    )

    # Verify methods exist
    assert hasattr(template, 'update_html_from_file')
    assert hasattr(template, 'update_css_from_file')
    assert hasattr(template, 'create_file_from_content')
    assert hasattr(template, 'has_files')
    assert hasattr(template, 'has_inline_content')

    # Verify properties
    assert template.has_inline_content
    assert not template.has_files

    # Cleanup
    template.delete()


def test_performance_metrics_available():
    """Performance metrics should be available."""
    from ceptor_ai.communication.email.models import EmailTemplate

    template = EmailTemplate.objects.create(
        name="test_metrics",
        subject_template="Test",
        html_content="<p>Test</p>",
    )

    # Verify metrics fields exist
    assert hasattr(template, 'open_rate')
    assert hasattr(template, 'click_rate')
    assert hasattr(template, 'conversion_rate')
    assert hasattr(template, 'bounce_rate')
    assert hasattr(template, 'render_count')

    # Verify default values
    assert template.open_rate == 0.0
    assert template.click_rate == 0.0
    assert template.render_count == 0

    # Test update_metrics method
    template.update_metrics(opens=50, clicks=25, conversions=10, bounces=5, deliveries=100)
    assert template.open_rate == 50.0
    assert template.click_rate == 25.0
    assert template.conversion_rate == 10.0
    assert template.bounce_rate == 5.0

    # Cleanup
    template.delete()


def test_website_signal_compatibility():
    """Verify compatibility with website signal handlers."""
    from ceptor_ai.communication.email.models import EmailTemplate

    # This is how websites import it
    template = EmailTemplate.objects.create(
        name="test_website_compat",
        subject_template="Test",
        html_content="<p>Test</p>",
    )

    # Verify methods used in signals exist
    assert hasattr(template, 'update_html_from_file')
    assert hasattr(template, 'update_css_from_file')
    assert hasattr(template, 'is_default')
    assert hasattr(template, 'is_system')
    assert hasattr(template, 'template_type')
    assert hasattr(template, 'language')

    # Cleanup
    template.delete()


def test_app_label_is_canonical():
    """Verify app_label is ceptor_ai (canonical)."""
    from ceptor_ai.communication.email.models import EmailTemplate

    assert EmailTemplate._meta.app_label == 'ceptor_ai'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
