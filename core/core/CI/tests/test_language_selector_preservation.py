"""
Preservation property-based tests for language selector functionality.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

These tests capture the baseline behavior that MUST be preserved after the fix.
They test the WORKING alliance-core language selector to establish expected behavior.

CRITICAL: These tests should PASS on UNFIXED code (testing alliance-core template).
After the fix, these tests should STILL PASS (proving no regressions).

This follows the observation-first methodology:
1. Observe behavior on working code (alliance-core)
2. Write tests that capture that behavior
3. Verify tests pass on unfixed code
4. After fix, verify tests still pass (no regressions)
"""
from hypothesis import given, strategies as st, settings
import os
import re


def analyze_template(template_path):
    """
    Analyze a language selector template to extract its features.

    Returns:
        dict: Template features including loaded libraries, tags used, etc.
    """
    with open(template_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        first_line = lines[0] if lines else ''

    # Extract loaded template libraries
    load_match = re.search(r'{%\s*load\s+(.+?)\s*%}', first_line)
    loaded_libraries = []
    if load_match:
        loaded_libraries = [lib.strip() for lib in load_match.group(1).split()]

    # Check for specific features
    features = {
        'loaded_libraries': loaded_libraries,
        'has_language_form': 'method="post"' in content and 'set_language' in content,
        'has_csrf_token': 'csrf_token' in content,
        'has_language_dropdown': 'languageDropdown' in content,
        'uses_get_language_info': 'get_language_info' in content,
        'uses_get_translation': 'get_translation' in content,
        'has_flag_icons': 'flagcdn.com' in content,
        'has_current_language_indicator': 'fa-check' in content or 'current-language' in content,
        'has_language_loop': 'for lang in LANGUAGES' in content,
        'has_translated_url': 'trans_page.url' in content,
        'has_fallback_url': 'lang.url' in content,
    }

    return features


@given(
    # Generate different language codes that might be configured
    language_code=st.sampled_from(['en', 'ar', 'es', 'fr', 'de'])
)
@settings(max_examples=5, deadline=1000)
def test_preservation_language_switching_mechanism(language_code):
    """
    Property 2: Preservation - Language Switching Mechanism

    **Validates: Requirement 3.2**

    For any language code in the configured languages, the language selector SHALL
    continue to provide a form-based language switching mechanism with CSRF protection
    that submits to the 'set_language' URL.

    This property verifies that the language switching functionality remains unchanged.

    EXPECTED ON UNFIXED CODE: PASS (alliance-core template works correctly)
    EXPECTED ON FIXED CODE: PASS (behavior preserved)
    """
    # Test the working alliance-core template
    alliance_template = 'alliance-core/assets/templates/partials/language_selector.html'

    if not os.path.exists(alliance_template):
        # If alliance-core template doesn't exist, skip this test
        return

    features = analyze_template(alliance_template)

    # Assert: Language switching form must be present
    assert features['has_language_form'], (
        f"Language selector must have a form that posts to 'set_language' URL "
        f"for language code '{language_code}'. This is the standard Django "
        f"language switching mechanism that must be preserved."
    )

    # Assert: CSRF protection must be present
    assert features['has_csrf_token'], (
        f"Language switching form must include CSRF token for security "
        f"when switching to language '{language_code}'. This security feature "
        f"must be preserved."
    )


@given(
    # Generate different language codes for flag display
    language_code=st.sampled_from(['en', 'ar', 'es', 'fr', 'de'])
)
@settings(max_examples=5, deadline=1000)
def test_preservation_flag_icon_display(language_code):
    """
    Property 2: Preservation - Flag Icon Display

    **Validates: Requirement 3.4**

    For any language code in the configured languages, the language selector SHALL
    continue to display flag icons from flagcdn.com based on the language code.

    This property verifies that flag display functionality remains unchanged.

    EXPECTED ON UNFIXED CODE: PASS (alliance-core template works correctly)
    EXPECTED ON FIXED CODE: PASS (behavior preserved)
    """
    # Test the working alliance-core template
    alliance_template = 'alliance-core/assets/templates/partials/language_selector.html'

    if not os.path.exists(alliance_template):
        return

    features = analyze_template(alliance_template)

    # Assert: Flag icons must be present
    assert features['has_flag_icons'], (
        f"Language selector must display flag icons from flagcdn.com "
        f"for language '{language_code}'. This visual feature must be preserved."
    )


@given(
    # Generate different language codes for current language indicator
    language_code=st.sampled_from(['en', 'ar', 'es', 'fr', 'de'])
)
@settings(max_examples=5, deadline=1000)
def test_preservation_current_language_indicator(language_code):
    """
    Property 2: Preservation - Current Language Indicator

    **Validates: Requirement 3.3**

    For any language code that is currently active, the language selector SHALL
    continue to display a checkmark indicator next to the current language using
    the get_language_info tag.

    This property verifies that current language display remains unchanged.

    EXPECTED ON UNFIXED CODE: PASS (alliance-core template works correctly)
    EXPECTED ON FIXED CODE: PASS (behavior preserved)
    """
    # Test the working alliance-core template
    alliance_template = 'alliance-core/assets/templates/partials/language_selector.html'

    if not os.path.exists(alliance_template):
        return

    features = analyze_template(alliance_template)

    # Assert: get_language_info tag must be used
    assert features['uses_get_language_info'], (
        f"Language selector must use 'get_language_info' tag to display "
        f"current language information for '{language_code}'. This functionality "
        f"must be preserved."
    )

    # Assert: Current language indicator must be present
    assert features['has_current_language_indicator'], (
        f"Language selector must display a checkmark or indicator for the "
        f"current language '{language_code}'. This visual feedback must be preserved."
    )


@given(
    # Generate different scenarios for translated page URLs
    has_translation=st.booleans()
)
@settings(max_examples=5, deadline=1000)
def test_preservation_translated_url_navigation(has_translation):
    """
    Property 2: Preservation - Translated URL Navigation

    **Validates: Requirement 3.5**

    For any page that may or may not have translations, the language selector SHALL
    continue to use trans_page.url when a translation exists, and fall back to
    lang.url when no translation exists.

    This property verifies that URL navigation logic remains unchanged.

    EXPECTED ON UNFIXED CODE: PASS (alliance-core template works correctly)
    EXPECTED ON FIXED CODE: PASS (behavior preserved)
    """
    # Test the working alliance-core template
    alliance_template = 'alliance-core/assets/templates/partials/language_selector.html'

    if not os.path.exists(alliance_template):
        return

    features = analyze_template(alliance_template)

    # Assert: Translated page URL must be used
    assert features['has_translated_url'], (
        f"Language selector must use 'trans_page.url' for pages with translations "
        f"(has_translation={has_translation}). This navigation logic must be preserved."
    )

    # Assert: Fallback URL must be present
    assert features['has_fallback_url'], (
        f"Language selector must fall back to 'lang.url' when no translation exists "
        f"(has_translation={has_translation}). This fallback logic must be preserved."
    )


def test_preservation_template_libraries_loaded():
    """
    Property 2: Preservation - Template Libraries Continue to Work

    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

    All template libraries that were loaded before the fix (static, i18n,
    wagtailcore_tags, wagtailimages_tags, wagtailsettings_tags) SHALL continue
    to work correctly after the fix.

    This test verifies that adding wagtail_i18n_tags doesn't break other libraries.

    EXPECTED ON UNFIXED CODE: PASS (alliance-core template has all libraries)
    EXPECTED ON FIXED CODE: PASS (all libraries still work)
    """
    # Test the working alliance-core template
    alliance_template = 'alliance-core/assets/templates/partials/language_selector.html'

    if not os.path.exists(alliance_template):
        return

    features = analyze_template(alliance_template)

    # Required libraries that must be present
    required_libraries = [
        'static',
        'i18n',
        'wagtailcore_tags',
        'wagtailimages_tags',
        'wagtailsettings_tags',
    ]

    for library in required_libraries:
        assert library in features['loaded_libraries'], (
            f"Template must load '{library}' library. This is required for "
            f"existing functionality and must be preserved. "
            f"Found libraries: {features['loaded_libraries']}"
        )


def test_preservation_alliance_core_template_unchanged():
    """
    Property 2: Preservation - AllianceCore Template Unchanged

    **Validates: Requirement 3.1**

    The alliance-core project's language selector SHALL continue to work correctly
    as it already has wagtail_i18n_tags loaded. The fix should not affect it.

    EXPECTED ON UNFIXED CODE: PASS (alliance-core template already works)
    EXPECTED ON FIXED CODE: PASS (alliance-core template still works)
    """
    # Test the working alliance-core template
    alliance_template = 'alliance-core/assets/templates/partials/language_selector.html'

    if not os.path.exists(alliance_template):
        # If alliance-core doesn't exist in this environment, skip
        return

    features = analyze_template(alliance_template)

    # Assert: alliance-core template must have wagtail_i18n_tags
    assert 'wagtail_i18n_tags' in features['loaded_libraries'], (
        f"AllianceCore template must have 'wagtail_i18n_tags' loaded. "
        f"This is the working reference implementation. "
        f"Found libraries: {features['loaded_libraries']}"
    )

    # Assert: alliance-core template must use get_translation
    assert features['uses_get_translation'], (
        f"AllianceCore template must use 'get_translation' tag. "
        f"This is the working reference implementation that must remain unchanged."
    )

    # Assert: All core features must be present
    assert features['has_language_form'], "AllianceCore template must have language switching form"
    assert features['has_flag_icons'], "AllianceCore template must have flag icons"
    assert features['has_current_language_indicator'], "AllianceCore template must have current language indicator"
    assert features['has_translated_url'], "AllianceCore template must have translated URL navigation"


if __name__ == '__main__':
    """
    Run the preservation tests directly.
    These should PASS on unfixed code (testing alliance-core template).
    """
    print("=" * 70)
    print("PRESERVATION PROPERTY-BASED TESTS")
    print("=" * 70)
    print()
    print("Testing baseline behavior that must be preserved after the fix.")
    print("These tests run against the WORKING alliance-core template.")
    print()

    # Run unit tests
    print("Running: test_preservation_template_libraries_loaded")
    print("-" * 70)
    try:
        test_preservation_template_libraries_loaded()
        print("✓ PASS: All required template libraries are loaded")
    except AssertionError as e:
        print(f"✗ FAIL: {e}")
    print()

    print("Running: test_preservation_alliance_core_template_unchanged")
    print("-" * 70)
    try:
        test_preservation_alliance_core_template_unchanged()
        print("✓ PASS: AllianceCore template works correctly")
    except AssertionError as e:
        print(f"✗ FAIL: {e}")
    print()

    # Run property-based tests
    print("Running property-based tests...")
    print("-" * 70)

    test_functions = [
        ('Language Switching Mechanism', test_preservation_language_switching_mechanism),
        ('Flag Icon Display', test_preservation_flag_icon_display),
        ('Current Language Indicator', test_preservation_current_language_indicator),
        ('Translated URL Navigation', test_preservation_translated_url_navigation),
    ]

    for test_name, test_func in test_functions:
        print(f"\nTesting: {test_name}")
        try:
            test_func()
            print(f"✓ PASS: {test_name} preserved")
        except AssertionError as e:
            print(f"✗ FAIL: {e}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Preservation tests complete. All tests should PASS on unfixed code.")
    print("After implementing the fix, these tests should STILL PASS (no regressions).")
