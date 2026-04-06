"""
Bug condition exploration test for language selector template tag issue.

**Validates: Requirements 2.1, 2.2, 2.3**

This test MUST FAIL on unfixed code to confirm the bug exists.
The test encodes the expected behavior - it will pass after the fix is implemented.
"""
from django.test import TestCase, Client
from django.template import TemplateSyntaxError
from django.template.loader import get_template
from django.contrib.auth import get_user_model
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase as HypothesisTestCase

User = get_user_model()


class LanguageSelectorBugConditionTest(HypothesisTestCase):
    """
    Bug condition exploration test for Property 1: Bug Condition - Template Renders Successfully

    **Property 1: Bug Condition - Template Renders Successfully**
    **Validates: Requirements 2.1, 2.2, 2.3**

    For any template render request where the structa/core language_selector.html template
    is included, the fixed template SHALL load the wagtail_i18n_tags library and successfully
    execute the get_translation tag without raising a TemplateSyntaxError, allowing the page
    to render with HTTP 200.

    EXPECTED OUTCOME ON UNFIXED CODE: Test FAILS
    - TemplateSyntaxError: "Invalid block tag on line 25: 'get_translation'"
    - HTTP 500 error when accessing pages with language selector
    - Missing wagtail_i18n_tags in load statement

    EXPECTED OUTCOME ON FIXED CODE: Test PASSES
    - Template renders successfully with HTTP 200
    - No TemplateSyntaxError
    - Language selector is rendered correctly
    """

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create a test user for authenticated requests
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_homepage_renders_successfully(self):
        """
        Test that the homepage renders successfully without TemplateSyntaxError.

        **Validates: Requirements 2.1, 2.3**

        EXPECTED ON UNFIXED CODE: HTTP 500 with TemplateSyntaxError
        EXPECTED ON FIXED CODE: HTTP 200 with successful render
        """
        # Access the homepage
        response = self.client.get('/')

        # Assert: Template renders successfully with HTTP 200
        self.assertEqual(
            response.status_code, 200,
            f"Homepage should render with HTTP 200, got {response.status_code}. "
            f"This likely means the get_translation tag is not registered."
        )

        # Assert: No TemplateSyntaxError in response
        self.assertNotIn(
            'TemplateSyntaxError', str(response.content),
            "Homepage should not have TemplateSyntaxError for 'get_translation' tag"
        )

        # Assert: Language selector is rendered (contains language dropdown)
        self.assertIn(
            b'languageDropdown', response.content,
            "Language selector should be rendered on the homepage"
        )

    def test_language_selector_template_loads_wagtail_i18n_tags(self):
        """
        Test that the language_selector.html template has wagtail_i18n_tags loaded.

        **Validates: Requirements 2.2**

        EXPECTED ON UNFIXED CODE: wagtail_i18n_tags NOT in load statement
        EXPECTED ON FIXED CODE: wagtail_i18n_tags in load statement
        """
        # Read the template file
        template_path = 'structa/core/assets/templates/partials/language_selector.html'

        with open(template_path, 'r') as f:
            first_line = f.readline()

        # Assert: Line 1 contains 'wagtail_i18n_tags' in the load statement
        self.assertIn(
            'wagtail_i18n_tags', first_line,
            f"Line 1 of {template_path} should contain 'wagtail_i18n_tags' in the load statement. "
            f"Found: {first_line.strip()}"
        )

    @given(
        language_code=st.sampled_from(['en', 'ar', 'es', 'fr', 'de'])
    )
    @settings(max_examples=5, deadline=5000)
    def test_language_selector_renders_for_different_languages(self, language_code):
        """
        Property-based test: Language selector renders successfully for any language.

        **Validates: Requirements 2.1, 2.2, 2.3**

        For any language code, when accessing a page with the language selector,
        the page should render successfully with HTTP 200.

        EXPECTED ON UNFIXED CODE: HTTP 500 with TemplateSyntaxError
        EXPECTED ON FIXED CODE: HTTP 200 with successful render
        """
        # Access homepage with language prefix
        response = self.client.get(f'/{language_code}/')

        # Assert: Template renders successfully with HTTP 200
        self.assertEqual(
            response.status_code, 200,
            f"Page with language '{language_code}' should render with HTTP 200, got {response.status_code}. "
            f"This likely means the get_translation tag is not registered."
        )

        # Assert: No TemplateSyntaxError
        self.assertNotIn(
            'TemplateSyntaxError', str(response.content),
            f"Page with language '{language_code}' should not have TemplateSyntaxError"
        )

        # Assert: Language selector is rendered
        self.assertIn(
            b'languageDropdown', response.content,
            f"Language selector should be rendered for language '{language_code}'"
        )
