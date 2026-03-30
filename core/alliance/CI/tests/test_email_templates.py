"""
Property-based tests for email template rendering system.

**Validates: Requirements 1.1, 4.1, 4.2, 4.6**
"""
import os
import re
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.template.loader import get_template, render_to_string
from django.test import TestCase, override_settings
from django.utils import timezone
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import from_model, TestCase as HypothesisTestCase

from apps.LMS.models.courses.info import Course
from apps.LMS.models.enrollment import Enrollment
from apps.handlers.services.email.service import EmailService

User = get_user_model()


class EmailTemplatePropertyTests(HypothesisTestCase):
    """
    Property-based tests for email template rendering system.

    **Property 1: Template System Completeness**
    **Validates: Requirements 1.1, 4.1, 4.2, 4.6**

    This test ensures that for any email template (welcome, password_reset,
    enrollment, completion), when rendered with valid context data, the template
    renders successfully without missing variables and includes all required
    content elements.
    """

    def setUp(self):
        """Set up test data."""
        self.email_service = EmailService()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Create instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123',
            first_name='John',
            last_name='Instructor'
        )

        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            instructor=self.instructor,
            price=Decimal('99.99'),
            duration=10,
            difficulty_level='beginner',
            is_published=True,
            has_certificate=True
        )

        # Create test enrollment
        self.enrollment = Enrollment.objects.create(
            student=self.user,
            course=self.course,
            payment_status='completed',
            status='active'
        )

    # Strategy for generating email template names
    @st.composite
    def email_template_strategy(draw):
        """Generate valid email template names."""
        templates = ['welcome', 'password_reset', 'enrollment', 'completion']
        return draw(st.sampled_from(templates))

    # Strategy for generating user data
    @st.composite
    def user_data_strategy(draw):
        """Generate valid user data for templates."""
        first_name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))))
        last_name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))))
        username = draw(st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
        email = draw(st.emails())

        return {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email
        }

    # Strategy for generating course data
    @st.composite
    def course_data_strategy(draw):
        """Generate valid course data for templates."""
        title = draw(st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
        duration = draw(st.integers(min_value=1, max_value=100))
        difficulty = draw(st.sampled_from(['beginner', 'intermediate', 'advanced']))
        has_certificate = draw(st.booleans())

        return {
            'title': title.strip(),
            'duration': duration,
            'difficulty_level': difficulty,
            'has_certificate': has_certificate
        }

    # Strategy for generating template context
    @st.composite
    def template_context_strategy(draw, template_name):
        """Generate valid context data for specific templates."""
        user_data = draw(EmailTemplatePropertyTests.user_data_strategy())
        course_data = draw(EmailTemplatePropertyTests.course_data_strategy())

        # Base context that all templates should have
        base_context = {
            'user': Mock(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                username=user_data['username'],
                email=user_data['email'],
                get_full_name=lambda: f"{user_data['first_name']} {user_data['last_name']}"
            ),
            'site_name': draw(st.text(min_size=3, max_size=50)),
            'year': draw(st.integers(min_value=2020, max_value=2030)),
            'unsubscribe_url': 'https://example.com/unsubscribe',
            'privacy_url': 'https://example.com/privacy'
        }

        # Template-specific context
        if template_name == 'welcome':
            base_context.update({
                'login_url': 'https://example.com/login'
            })
        elif template_name == 'password_reset':
            base_context.update({
                'reset_url': 'https://example.com/reset/token123',
                'expiry_hours': draw(st.integers(min_value=1, max_value=48))
            })
        elif template_name == 'enrollment':
            instructor_mock = Mock(
                first_name='John',
                last_name='Instructor',
                username='instructor',
                get_full_name=lambda: 'John Instructor'
            )
            course_mock = Mock(
                title=course_data['title'],
                duration=course_data['duration'],
                get_difficulty_level_display=course_data['difficulty_level'].title(),
                has_certificate=course_data['has_certificate'],
                instructor=instructor_mock,
                objectives_list=['Learn basics', 'Practice skills', 'Build projects']
            )
            base_context.update({
                'course': course_mock,
                'access_link': 'https://example.com/course/access',
                'start_date': draw(st.datetimes(min_value=datetime.now(), max_value=datetime.now() + timedelta(days=30)))
            })
        elif template_name == 'completion':
            course_mock = Mock(
                title=course_data['title'],
                instructor=Mock(
                    get_full_name=lambda: 'John Instructor',
                    username='instructor'
                )
            )
            base_context.update({
                'course': course_mock,
                'course_title': course_data['title'],
                'completion_date': draw(st.datetimes(min_value=datetime.now() - timedelta(days=30), max_value=datetime.now())),
                'certificate_url': 'https://example.com/certificate/123' if course_data['has_certificate'] else None,
                'final_score': draw(st.integers(min_value=70, max_value=100)) if draw(st.booleans()) else None,
                'name': user_data['first_name']
            })

        return base_context

    @given(template_name=email_template_strategy())
    @settings(max_examples=10, deadline=3000)
    def test_template_system_completeness(self, template_name):
        """
        **Property 1: Template System Completeness**
        **Validates: Requirements 1.1, 4.1, 4.2, 4.6**

        For any email template (welcome, password_reset, enrollment, completion),
        when rendered with valid context data, the template:
        1. Renders successfully without exceptions
        2. Contains no missing variable references ({{ undefined_var }})
        3. Includes all required content elements
        4. Produces valid HTML structure
        5. Contains expected template-specific content
        """
        # Generate valid context for this template
        context = self.template_context_strategy(template_name)

        try:
            # Test 1: Template renders successfully without exceptions
            template_path = f"email/{template_name}.html"
            rendered_content = render_to_string(template_path, context)

            # Test 2: No missing variable references
            # Look for Django template variable syntax that wasn't resolved
            missing_vars = re.findall(r'\{\{\s*([^}]+)\s*\}\}', rendered_content)
            filtered_missing = [var for var in missing_vars if not any(
                keyword in var.lower() for keyword in ['default', 'date', 'time', 'block', 'load', 'csrf']
            )]

            self.assertEqual(
                len(filtered_missing), 0,
                f"Template {template_name} has unresolved variables: {filtered_missing}"
            )

            # Test 3: Contains required content elements
            self._assert_required_content_elements(template_name, rendered_content, context)

            # Test 4: Valid HTML structure
            self._assert_valid_html_structure(rendered_content)

            # Test 5: Template-specific content validation
            self._assert_template_specific_content(template_name, rendered_content, context)

        except Exception as e:
            self.fail(f"Template {template_name} failed to render with context {list(context.keys())}: {str(e)}")

    def _assert_required_content_elements(self, template_name, content, context):
        """Assert that template contains all required content elements."""
        # All email templates should have these elements
        self.assertIn('<!DOCTYPE html>', content, f"Template {template_name} missing DOCTYPE")
        self.assertIn('<html', content, f"Template {template_name} missing html tag")
        self.assertIn('<head>', content, f"Template {template_name} missing head section")
        self.assertIn('<body>', content, f"Template {template_name} missing body section")

        # Should contain site name
        site_name = context.get('site_name', 'Our Platform')
        self.assertIn(site_name, content, f"Template {template_name} missing site name")

        # Should contain user reference
        user = context.get('user')
        if user and hasattr(user, 'first_name') and user.first_name:
            self.assertIn(user.first_name, content, f"Template {template_name} missing user first name")

    def _assert_valid_html_structure(self, content):
        """Assert that rendered content has valid HTML structure."""
        # Basic HTML validation
        self.assertIn('<html', content, "Missing html opening tag")
        self.assertIn('</html>', content, "Missing html closing tag")
        self.assertIn('<head>', content, "Missing head opening tag")
        self.assertIn('</head>', content, "Missing head closing tag")
        self.assertIn('<body>', content, "Missing body opening tag")
        self.assertIn('</body>', content, "Missing body closing tag")

        # Should have proper email structure
        self.assertIn('email-container', content, "Missing email container structure")
        self.assertIn('email-header', content, "Missing email header")
        self.assertIn('email-body', content, "Missing email body")
        self.assertIn('email-footer', content, "Missing email footer")

    def _assert_template_specific_content(self, template_name, content, context):
        """Assert template-specific content requirements."""
        if template_name == 'welcome':
            self.assertIn('Welcome', content, "Welcome template missing welcome message")
            login_url = context.get('login_url')
            if login_url:
                self.assertIn(login_url, content, "Welcome template missing login URL")

        elif template_name == 'password_reset':
            self.assertIn('password', content.lower(), "Password reset template missing password reference")
            self.assertIn('reset', content.lower(), "Password reset template missing reset reference")
            reset_url = context.get('reset_url')
            if reset_url:
                self.assertIn(reset_url, content, "Password reset template missing reset URL")

        elif template_name == 'enrollment':
            self.assertIn('enrollment', content.lower(), "Enrollment template missing enrollment reference")
            course = context.get('course')
            if course and hasattr(course, 'title'):
                self.assertIn(course.title, content, "Enrollment template missing course title")
            access_link = context.get('access_link')
            if access_link:
                self.assertIn(access_link, content, "Enrollment template missing access link")

        elif template_name == 'completion':
            self.assertIn('complet', content.lower(), "Completion template missing completion reference")
            self.assertIn('congratulat', content.lower(), "Completion template missing congratulations")
            course_title = context.get('course_title') or (context.get('course') and context['course'].title)
            if course_title:
                self.assertIn(course_title, content, "Completion template missing course title")

    @given(
        user_data=user_data_strategy(),
        course_data=course_data_strategy()
    )
    @settings(max_examples=10, deadline=3000)
    def test_email_service_template_integration(self, user_data, course_data):
        """
        Test that EmailService properly integrates with templates.
        **Validates: Requirements 1.1, 1.5**
        """
        # Test welcome email
        with patch('apps.handlers.services.email.service.render_to_string') as mock_render:
            mock_render.return_value = f"<html><body>Welcome {user_data['first_name']}!</body></html>"

            result = self.email_service.send_welcome(
                user_email=user_data['email'],
                user_name=user_data['first_name']
            )

            # Should call render_to_string with correct template and context
            mock_render.assert_called()
            args, kwargs = mock_render.call_args
            self.assertEqual(args[0], "email/welcome.html")
            self.assertIn('name', args[1])
            self.assertEqual(args[1]['name'], user_data['first_name'])

    def test_all_email_templates_exist(self):
        """
        Verify that all required email templates exist in the filesystem.
        **Validates: Requirements 1.1, 4.1**
        """
        required_templates = ['welcome', 'password_reset', 'enrollment', 'completion']

        for template_name in required_templates:
            template_path = f"email/{template_name}.html"
            try:
                template = get_template(template_path)
                self.assertIsNotNone(template, f"Template {template_path} should exist")
            except Exception as e:
                self.fail(f"Required template {template_path} is missing or invalid: {str(e)}")

    def test_base_email_template_structure(self):
        """
        Test that base email template provides proper structure.
        **Validates: Requirements 4.1, 4.2**
        """
        try:
            base_template = get_template("email/base_email.html")
            self.assertIsNotNone(base_template)

            # Render with minimal context
            context = {
                'site_name': 'Test Site',
                'year': 2024
            }

            rendered = base_template.render(context)

            # Should have proper email structure
            self.assertIn('email-container', rendered)
            self.assertIn('email-header', rendered)
            self.assertIn('email-body', rendered)
            self.assertIn('email-footer', rendered)

        except Exception as e:
            self.fail(f"Base email template failed: {str(e)}")

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_template_rendering_with_real_models(self):
        """
        Test template rendering with actual Django model instances.
        **Validates: Requirements 1.1, 3.1, 3.2**
        """
        # Test enrollment template with real models
        context = {
            'user': self.user,
            'course': self.course,
            'site_name': 'Test LMS',
            'access_link': 'https://example.com/course/test-course',
            'start_date': timezone.now() + timedelta(days=7)
        }

        try:
            rendered = render_to_string("email/enrollment.html", context)

            # Should contain actual model data
            self.assertIn(self.user.first_name, rendered)
            self.assertIn(self.course.title, rendered)
            self.assertIn(self.instructor.get_full_name(), rendered)

            # Should not have unresolved variables
            unresolved = re.findall(r'\{\{\s*[^}]+\s*\}\}', rendered)
            # Filter out intentional template tags
            actual_unresolved = [var for var in unresolved if not any(
                keyword in var for keyword in ['block', 'endblock', 'load', 'csrf', 'default', 'date']
            )]
            self.assertEqual(len(actual_unresolved), 0, f"Unresolved variables: {actual_unresolved}")

        except Exception as e:
            self.fail(f"Template rendering with real models failed: {str(e)}")
