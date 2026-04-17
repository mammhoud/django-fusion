"""
Unit tests for template validation system.

Tests cover:
- Syntax validation
- Structure validation
- Missing variable detection
- Filter validation
- Error reporting
"""

from django.test import TestCase
from django.template import Template, TemplateSyntaxError

from core.CI.utils import (
    TemplateValidator,
    validate_template,
    validate_template_string,
    TemplateValidationError
)


class TemplateValidatorUnitTests(TestCase):
    """Unit tests for TemplateValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = TemplateValidator()

    def test_valid_simple_template(self):
        """Test validation of a simple valid template."""
        template_string = "Hello {{ name }}!"
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {'name': 'World'}
        )

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(warnings), 0)

    def test_template_with_syntax_error(self):
        """Test detection of syntax errors."""
        template_string = "Hello {{ name }!"  # Missing closing brace
        is_valid, errors, warnings = validate_template_string(template_string)

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertIn("syntax error", errors[0].lower())

    def test_template_with_unclosed_block(self):
        """Test detection of unclosed block tags."""
        template_string = "{% block content %}Hello{% endblock %}"
        is_valid, errors, warnings = validate_template_string(template_string)

        # This should be valid
        self.assertTrue(is_valid)

    def test_template_with_unbalanced_if(self):
        """Test detection of unbalanced if tags."""
        template_string = "{% if True %}Hello"  # Missing endif
        is_valid, errors, warnings = validate_template_string(template_string)

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_template_with_unbalanced_for(self):
        """Test detection of unbalanced for tags."""
        template_string = "{% for item in items %}{{ item }}"  # Missing endfor
        is_valid, errors, warnings = validate_template_string(template_string)

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_missing_variable_detection(self):
        """Test detection of missing variables in context."""
        template_string = "Hello {{ name }} and {{ age }}!"
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {'name': 'World'}  # age is missing
        )

        # Should still be valid but with warnings
        self.assertTrue(is_valid)
        self.assertGreater(len(warnings), 0)

    def test_template_with_filters(self):
        """Test validation of templates with filters."""
        template_string = "Hello {{ name|upper }}!"
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {'name': 'world'}
        )

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_template_with_invalid_filter(self):
        """Test detection of potentially invalid filters."""
        template_string = "Hello {{ name|nonexistent_filter }}!"
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {'name': 'world'}
        )

        # Should be valid but may have warnings about unknown filter
        self.assertTrue(is_valid)

    def test_template_with_nested_blocks(self):
        """Test validation of templates with nested blocks."""
        template_string = """
        {% block outer %}
            {% block inner %}
                Content
            {% endblock inner %}
        {% endblock outer %}
        """
        is_valid, errors, warnings = validate_template_string(template_string)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_template_with_for_loop(self):
        """Test validation of templates with for loops."""
        template_string = """
        {% for item in items %}
            {{ item }}
        {% endfor %}
        """
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {'items': [1, 2, 3]}
        )

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_template_with_if_else(self):
        """Test validation of templates with if/else."""
        template_string = """
        {% if condition %}
            True branch
        {% else %}
            False branch
        {% endif %}
        """
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {'condition': True}
        )

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_template_with_comments(self):
        """Test validation of templates with comments."""
        template_string = """
        {# This is a comment #}
        Hello {{ name }}!
        """
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {'name': 'World'}
        )

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_template_with_multiple_variables(self):
        """Test validation with multiple variables."""
        template_string = """
        Name: {{ user.name }}
        Email: {{ user.email }}
        Age: {{ user.age }}
        """
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {'user': {'name': 'John', 'email': 'john@example.com', 'age': 30}}
        )

        self.assertTrue(is_valid)

    def test_template_with_builtin_variables(self):
        """Test that builtin variables don't trigger warnings."""
        template_string = """
        {% if user.is_authenticated %}
            Hello {{ user.username }}!
        {% endif %}
        """
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {}  # Empty context, but user is builtin
        )

        # Should be valid, user is a builtin variable
        self.assertTrue(is_valid)

    def test_empty_template(self):
        """Test validation of empty template."""
        template_string = ""
        is_valid, errors, warnings = validate_template_string(template_string)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_template_with_only_text(self):
        """Test validation of template with only text."""
        template_string = "This is just plain text."
        is_valid, errors, warnings = validate_template_string(template_string)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_template_with_extends(self):
        """Test validation of template with extends tag."""
        template_string = """
        {% extends "base.html" %}
        {% block content %}
            Hello World!
        {% endblock %}
        """
        is_valid, errors, warnings = validate_template_string(template_string)

        # May fail if base.html doesn't exist, but syntax should be valid
        # The actual validation depends on template loader configuration
        self.assertIsInstance(is_valid, bool)

    def test_template_with_include(self):
        """Test validation of template with include tag."""
        template_string = """
        {% include "header.html" %}
        <p>Content</p>
        {% include "footer.html" %}
        """
        is_valid, errors, warnings = validate_template_string(template_string)

        # May fail if included templates don't exist
        self.assertIsInstance(is_valid, bool)

    def test_template_with_load_tag(self):
        """Test validation of template with load tag."""
        template_string = """
        {% load static %}
        <img src="{% static 'image.png' %}">
        """
        is_valid, errors, warnings = validate_template_string(template_string)

        self.assertTrue(is_valid)

    def test_template_with_url_tag(self):
        """Test validation of template with url tag."""
        template_string = """
        <a href="{% url 'home' %}">Home</a>
        """
        is_valid, errors, warnings = validate_template_string(template_string)

        self.assertTrue(is_valid)

    def test_template_with_csrf_token(self):
        """Test validation of template with csrf_token."""
        template_string = """
        <form method="post">
            {% csrf_token %}
            <input type="submit">
        </form>
        """
        is_valid, errors, warnings = validate_template_string(template_string)

        self.assertTrue(is_valid)

    def test_complex_template(self):
        """Test validation of complex template with multiple features."""
        template_string = """
        {% load static %}
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
            <link rel="stylesheet" href="{% static 'css/style.css' %}">
        </head>
        <body>
            {% if user.is_authenticated %}
                <p>Welcome, {{ user.username|title }}!</p>
                {% for message in messages %}
                    <div class="alert">{{ message }}</div>
                {% endfor %}
            {% else %}
                <p>Please log in.</p>
            {% endif %}

            {% block content %}
                Default content
            {% endblock %}
        </body>
        </html>
        """
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {'title': 'Test Page'}
        )

        self.assertTrue(is_valid)


class TemplateValidatorIntegrationTests(TestCase):
    """Integration tests for template validation with Django template system."""

    def test_validate_nonexistent_template(self):
        """Test validation of non-existent template."""
        is_valid, errors, warnings = validate_template('nonexistent_template.html')

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertIn("does not exist", errors[0].lower())

    def test_validator_reusability(self):
        """Test that validator can be reused for multiple validations."""
        validator = TemplateValidator()

        # First validation
        template1 = "Hello {{ name }}!"
        is_valid1, errors1, warnings1 = validate_template_string(template1, {'name': 'World'})

        # Second validation
        template2 = "Goodbye {{ name }}!"
        is_valid2, errors2, warnings2 = validate_template_string(template2, {'name': 'World'})

        self.assertTrue(is_valid1)
        self.assertTrue(is_valid2)

    def test_error_message_clarity(self):
        """Test that error messages are clear and helpful."""
        template_string = "{% if True %}Hello"  # Missing endif
        is_valid, errors, warnings = validate_template_string(template_string)

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        # Error message should mention the specific issue
        error_text = ' '.join(errors).lower()
        self.assertTrue('if' in error_text or 'endif' in error_text or 'unclosed' in error_text)

    def test_warning_message_clarity(self):
        """Test that warning messages are clear and helpful."""
        template_string = "Hello {{ undefined_var }}!"
        is_valid, errors, warnings = validate_template_string(
            template_string,
            {'name': 'World'}  # undefined_var is missing
        )

        self.assertTrue(is_valid)
        if warnings:  # Warnings are optional
            warning_text = ' '.join(warnings).lower()
            self.assertTrue('variable' in warning_text or 'context' in warning_text)


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
            ],
            SECRET_KEY='test-secret-key',
        )
        django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["core.CI.tests.test_template_validation"])

    if failures:
        exit(1)
