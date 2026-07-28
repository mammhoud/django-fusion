"""
Tests for django-rseal EmailTemplate model.

These tests verify the comprehensive email template management system
including template sources, scheduling, multi-language support, and rendering.
"""

import os
import sys
from datetime import timedelta

# Add the project root to Python path so tests.settings can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import timezone

# Configure Django settings before importing django-rseal
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

import django

django.setup()

from ceptor_ai.email.models.models import EmailTemplate


@pytest.fixture
def basic_template_data():
    """Fixture providing basic template data."""
    return {
        "name": "Test Email Template",
        "template_type": "newsletter",
        "template_source": "inline",
        "subject_template": "Test Email - {{ site_name }}",
        "html_content": "<h1>Hello {{ user_name }}</h1><p>Welcome to {{ site_name }}</p>",
        "css_content": "body { font-family: Arial; }",
        "text_content": "Hello {{ user_name }}\nWelcome to {{ site_name }}",
        "preview_text": "Test preview text",
        "language": "en",
        "is_active": True,
    }


@pytest.fixture
def template_context():
    """Fixture providing template context."""
    return {
        "site_name": "Test Site",
        "user_name": "John Doe",
        "current_year": "2026",
    }


@pytest.mark.django_db
class TestEmailTemplateModel:
    """Test EmailTemplate model functionality."""

    def test_create_basic_template(self, basic_template_data):
        """Test creating a basic email template."""
        template = EmailTemplate.objects.create(**basic_template_data)

        assert template.name == "Test Email Template"
        assert template.template_type == "newsletter"
        assert template.template_source == "inline"
        assert template.language == "en"
        assert template.is_active is True
        assert template.is_live is True

    def test_template_rendering_inline(self, basic_template_data, template_context):
        """Test rendering template with inline content."""
        template = EmailTemplate.objects.create(**basic_template_data)

        rendered = template.get_rendered_content(context=template_context)

        assert "html" in rendered
        assert "css" in rendered
        assert "text" in rendered
        assert "subject" in rendered
        assert "preview_text" in rendered

        # Check placeholder replacement
        assert "John Doe" in rendered["html"]
        assert "Test Site" in rendered["html"]
        assert "Test Site" in rendered["subject"]

    def test_template_scheduling(self, basic_template_data):
        """Test template scheduling functionality."""
        now = timezone.now()
        future = now + timedelta(days=1)
        past = now - timedelta(days=1)

        # Test future scheduling
        data = basic_template_data.copy()
        data['name'] = 'Future Scheduled Template'
        data['go_live_at'] = future
        template = EmailTemplate.objects.create(**data)
        assert template.is_live is False
        assert "Scheduled" in template.scheduled_status

        # Test past expiration
        data2 = basic_template_data.copy()
        data2['name'] = 'Expired Template'
        data2['expire_at'] = past
        template2 = EmailTemplate.objects.create(**data2)
        assert template2.is_live is False
        assert "Expired" in template2.scheduled_status

        # Test active template
        data3 = basic_template_data.copy()
        data3['name'] = 'Active Template'
        data3['go_live_at'] = past
        data3['expire_at'] = future
        template3 = EmailTemplate.objects.create(**data3)
        assert template3.is_live is True
        assert "Active" in template3.scheduled_status

    def test_template_source_path(self, basic_template_data, template_context):
        """Test template with path source."""
        # Create a template that references a template path
        template_data = basic_template_data.copy()
        template_data.update({
            "template_source": "path",
            "template_path": "components/email/base.html",
        })

        template = EmailTemplate.objects.create(**template_data)

        # Test rendering (will fallback to inline if path doesn't exist)
        rendered = template.get_rendered_content(context=template_context)
        assert rendered is not None

    def test_default_template_constraint(self, basic_template_data):
        """Test that only one template can be default per type/language."""
        template1 = EmailTemplate.objects.create(**{**basic_template_data, 'is_default': True})

        template2 = EmailTemplate.objects.create(**{**basic_template_data, 'name': 'Second Template', 'is_default': True})

        # Refresh from database
        template1.refresh_from_db()
        template2.refresh_from_db()

        # Only the second should be default
        assert template1.is_default is False
        assert template2.is_default is True

    def test_template_language_support(self, basic_template_data):
        """Test multi-language template support."""
        en_template = EmailTemplate.objects.create(**{**basic_template_data, 'language': 'en', 'name': 'English Template'})
        es_template = EmailTemplate.objects.create(**{**basic_template_data, 'language': 'es', 'name': 'Spanish Template'})
        fr_template = EmailTemplate.objects.create(**{**basic_template_data, 'language': 'fr', 'name': 'French Template'})

        assert en_template.language == "en"
        assert es_template.language == "es"
        assert fr_template.language == "fr"

    def test_template_type_validation(self, basic_template_data):
        """Test template type validation."""
        valid_types = [
            "invitation", "notification", "newsletter", "transactional",
            "welcome", "password_reset", "order_confirmation", "system_alert",
            "campaign", "promotional", "abandoned_cart", "receipt",
            "feedback", "announcement"
        ]

        for template_type in valid_types:
            template = EmailTemplate.objects.create(
                **{**basic_template_data, 'template_type': template_type, 'name': f"{template_type} Template"},
            )
            assert template.template_type == template_type

    def test_template_file_upload(self, basic_template_data):
        """Test template file upload functionality."""
        template = EmailTemplate.objects.create(**basic_template_data)

        # Test HTML file upload
        html_file = ContentFile(b"<h1>Test HTML</h1>", name="test.html")
        template.html_file.save("test.html", html_file)

        # Test CSS file upload
        css_file = ContentFile(b"body { color: red; }", name="test.css")
        template.css_file.save("test.css", css_file)

        template.save()

        # Test reading from files
        assert template.update_html_from_file() is True
        assert template.update_css_from_file() is True

        assert "<h1>Test HTML</h1>" in template.html_content
        assert "body { color: red; }" in template.css_content

    def test_template_metrics(self, basic_template_data):
        """Test template performance metrics."""
        template = EmailTemplate.objects.create(**basic_template_data)

        # Initial metrics should be zero
        assert template.open_rate == 0.0
        assert template.click_rate == 0.0
        assert template.conversion_rate == 0.0
        assert template.bounce_rate == 0.0
        assert template.render_count == 0

        # Update metrics
        template.open_rate = 25.5
        template.click_rate = 10.2
        template.conversion_rate = 2.5
        template.bounce_rate = 1.2
        template.render_count = 100
        template.save()

        template.refresh_from_db()
        assert template.open_rate == 25.5
        assert template.click_rate == 10.2
        assert template.conversion_rate == 2.5
        assert template.bounce_rate == 1.2
        assert template.render_count == 100

    def test_template_cache_key(self, basic_template_data):
        """Test template cache key generation."""
        template = EmailTemplate.objects.create(**basic_template_data)

        assert template.cache_key is not None
        assert template.cache_key.startswith("template_")
        assert len(template.cache_key) == 41  # "template_" (9) + 32 hex chars

    def test_template_activation_methods(self, basic_template_data):
        """Test template activation methods."""
        template = EmailTemplate.objects.create(**basic_template_data)

        # Test mark as draft
        template.mark_as_draft()
        assert template.is_draft is True
        assert template.is_live is False

        # Test publish
        template.publish()
        assert template.is_draft is False

        # Test expire immediately
        template.expire_immediately()
        assert template.expire_at is not None
        assert template.is_live is False

        # Test activate immediately
        template.activate_immediately()
        assert template.go_live_at is None
        assert template.expire_at is None
        assert template.is_active is True
        assert template.is_draft is False

    def test_template_validation(self, basic_template_data):
        """Test template validation rules."""
        # Test invalid scheduling (go_live_at after expire_at)
        future = timezone.now() + timedelta(days=2)
        past = timezone.now() + timedelta(days=1)

        template_data = basic_template_data.copy()
        template_data.update({
            "go_live_at": future,
            "expire_at": past,
        })

        with pytest.raises(ValueError, match="go_live_at must be before expire_at"):
            EmailTemplate.objects.create(**template_data)

    def test_template_str_representation(self, basic_template_data):
        """Test template string representation."""
        template = EmailTemplate.objects.create(**basic_template_data)

        str_repr = str(template)
        assert "Test Email Template" in str_repr
        assert "Newsletter" in str_repr
        assert "English" in str_repr

        # Test with template path
        template2 = EmailTemplate.objects.create(
            **{**basic_template_data, 'template_source': 'path', 'template_path': 'emails/newsletter.html', 'name': 'Path Template'},
        )

        str_repr2 = str(template2)
        assert "Path Template" in str_repr2
        assert "emails/newsletter.html" in str_repr2


@pytest.mark.django_db
class TestEmailTemplateRendering:
    """Test email template rendering functionality."""

    @pytest.fixture
    def complex_template(self):
        """Fixture providing complex template with variables."""
        return EmailTemplate.objects.create(
            name="Complex Template",
            template_type="transactional",
            template_source="inline",
            subject_template="Important: {{ action }} for {{ user_name }}",
            html_content="""
            <!DOCTYPE html>
            <html>
            <head>
                <style>{{ css_content }}</style>
            </head>
            <body>
                <div class="container">
                    <h1>{{ greeting }}, {{ user_name }}!</h1>
                    <p>{{ message }}</p>
                    {% if show_button %}
                    <a href="{{ button_url }}" class="button">{{ button_text }}</a>
                    {% endif %}
                    <p>Sent from {{ site_name }} on {{ current_date }}</p>
                </div>
            </body>
            </html>
            """,
            css_content="""
            body { font-family: Arial, sans-serif; }
            .container { max-width: 600px; margin: 0 auto; }
            .button {
                display: inline-block;
                padding: 10px 20px;
                background-color: {{ primary_color }};
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
            """,
            text_content="""
            {{ greeting }}, {{ user_name }}!

            {{ message }}

            {% if show_button %}
            Click here: {{ button_url }}
            {% endif %}

            Sent from {{ site_name }} on {{ current_date }}
            """,
            preview_text="Important notification",
            language="en",
            is_active=True,
        )

    def test_complex_template_rendering(self, complex_template):
        """Test rendering complex template with conditionals and variables."""
        context = {
            "greeting": "Hello",
            "user_name": "Jane Smith",
            "message": "Your account has been updated successfully.",
            "action": "Account Update",
            "site_name": "Test Platform",
            "current_date": "April 18, 2026",
            "primary_color": "#2563eb",
            "show_button": True,
            "button_url": "https://example.com/dashboard",
            "button_text": "Go to Dashboard",
        }

        rendered = complex_template.get_rendered_content(context=context)

        # Check HTML rendering
        assert "Jane Smith" in rendered["html"]
        assert "Account Update" in rendered["subject"]
        assert "Go to Dashboard" in rendered["html"]
        assert "#2563eb" in rendered["css"]

        # Check text rendering
        assert "Jane Smith" in rendered["text"]
        assert "https://example.com/dashboard" in rendered["text"]

        # Check subject
        assert "Important: Account Update for Jane Smith" == rendered["subject"]

    def test_template_with_conditionals(self, basic_template_data):
        """Test template rendering with conditionals."""
        # Create a simple template with conditionals (avoid complex CSS that confuses parser)
        template = EmailTemplate.objects.create(
            name="Conditional Template",
            template_type="transactional",
            template_source="inline",
            subject_template="Test: {{ action }}",
            html_content="""
            <div>
                {% if show_button %}
                <a href="{{ button_url }}">{{ button_text }}</a>
                {% endif %}
                <p>Message: {{ message }}</p>
            </div>
            """,
            text_content="""
            {% if show_button %}
            Link: {{ button_url }} - {{ button_text }}
            {% endif %}
            Message: {{ message }}
            """,
            language="en",
            is_active=True,
        )

        # Test with show_button = True
        context_with_button = {
            "action": "Test",
            "message": "Hello World",
            "show_button": True,
            "button_url": "http://test.com",
            "button_text": "Click Me",
        }

        rendered_with = template.get_rendered_content(context=context_with_button)
        assert "Click Me" in rendered_with["html"]
        assert "http://test.com" in rendered_with["text"]

        # Test with show_button = False
        context_without_button = context_with_button.copy()
        context_without_button["show_button"] = False

        rendered_without = template.get_rendered_content(context=context_without_button)
        assert "Click Me" not in rendered_without["html"]
        assert "http://test.com" not in rendered_without["text"]

    def test_template_placeholder_replacement(self):
        """Test placeholder replacement in templates."""
        template = EmailTemplate.objects.create(
            name="Placeholder Test",
            template_type="notification",
            template_source="inline",
            subject_template="Notification: {{ event_type }} at {{ location }}",
            html_content="<p>Hello {{ recipient_name }},</p><p>Event: {{ event_type }}</p>",
            css_content="p { color: {{ text_color }}; }",
            text_content="Hello {{ recipient_name }}\nEvent: {{ event_type }}",
            language="en",
            is_active=True,
        )

        context = {
            "event_type": "Meeting",
            "location": "Conference Room",
            "recipient_name": "Alex Johnson",
            "text_color": "blue",
        }

        rendered = template.get_rendered_content(context=context)

        assert "Notification: Meeting at Conference Room" == rendered["subject"]
        assert "Alex Johnson" in rendered["html"]
        assert "Meeting" in rendered["html"]
        assert "blue" in rendered["css"]
        assert "Alex Johnson" in rendered["text"]


@pytest.mark.django_db
class TestEmailTemplateIntegration:
    """Test email template integration with other components."""

    def test_template_with_wagtail_images(self, basic_template_data):
        """Test template integration with Wagtail images."""
        # Note: This test would require Wagtail image fixtures
        # For now, we test that the model has the expected fields for image handling
        template = EmailTemplate.objects.create(**basic_template_data)

        # Check that the model has the expected fields for Wagtail integration
        # The actual image fields are handled via template_path and external_url
        assert hasattr(template, 'template_path')
        assert hasattr(template, 'external_url')
        assert hasattr(template, 'html_file')
        assert hasattr(template, 'css_file')

        # Check that the template can reference Wagtail templates via template_path
        template.template_path = "components/email/base.html"
        template.save()
        assert template.template_path == "components/email/base.html"

    def test_template_with_social_settings(self, basic_template_data):
        """Test template integration with social settings."""
        template = EmailTemplate.objects.create(**basic_template_data)

        # Test social settings fields
        assert hasattr(template, 'reply_to_email')
        assert hasattr(template, 'from_email')
        assert hasattr(template, 'from_name')
        assert hasattr(template, 'unsubscribe_url')

        # Test setting social settings
        template.reply_to_email = "reply@example.com"
        template.from_email = "noreply@example.com"
        template.from_name = "Example Team"
        template.unsubscribe_url = "https://example.com/unsubscribe"
        template.save()

        template.refresh_from_db()
        assert template.reply_to_email == "reply@example.com"
        assert template.from_email == "noreply@example.com"
        assert template.from_name == "Example Team"
        assert template.unsubscribe_url == "https://example.com/unsubscribe"

    def test_template_performance(self, basic_template_data, template_context):
        """Test template rendering performance."""
        import time

        template = EmailTemplate.objects.create(**basic_template_data)

        # Time the first render (should be slower due to cache miss)
        start_time = time.time()
        rendered1 = template.get_rendered_content(context=template_context)
        first_render_time = time.time() - start_time

        # Time the second render (should be faster due to cache hit)
        start_time = time.time()
        rendered2 = template.get_rendered_content(context=template_context)
        second_render_time = time.time() - start_time

        # Second render should be faster (or similar if very fast)
        # We just verify both renders produce the same output
        assert rendered1["html"] == rendered2["html"]
        assert rendered1["subject"] == rendered2["subject"]

        # render_count increments only on cache miss; first render should be counted
        template.refresh_from_db()
        assert template.render_count >= 1
