"""
Bug condition exploration property-based test for language selector template tag issue.

**Validates: Requirements 2.1, 2.2, 2.3**

This test MUST FAIL on unfixed code to confirm the bug exists.
The test encodes the expected behavior - it will pass after the fix is implemented.

CRITICAL: This is a bug exploration test for a bugfix spec.
- EXPECTED ON UNFIXED CODE: Test FAILS (proves bug exists)
- EXPECTED ON FIXED CODE: Test PASSES (proves bug is fixed)
"""
from hypothesis import given, strategies as st, settings
import os


def check_template_has_required_tags():
    """
    Check that the language_selector.html template has wagtail_i18n_tags loaded.

    Returns:
        tuple: (has_wagtail_i18n_tags, uses_get_translation, line_numbers)
    """
    template_path = 'assets/templates/partials/language_selector.html'

    with open(template_path, 'r') as f:
        first_line = f.readline()
        f.seek(0)
        content = f.read()

    has_wagtail_i18n_tags = 'wagtail_i18n_tags' in first_line
    uses_get_translation = 'get_translation' in content

    # Find line numbers where get_translation is used
    line_numbers = []
    for i, line in enumerate(content.split('\n'), 1):
        if 'get_translation' in line:
            line_numbers.append(i)

    return has_wagtail_i18n_tags, uses_get_translation, line_numbers


@given(
    # Generate different scenarios that would trigger template rendering
    page_context=st.sampled_from([
        {'page': 'homepage', 'language': 'en'},
        {'page': 'homepage', 'language': 'ar'},
        {'page': 'homepage', 'language': 'es'},
        {'page': 'content', 'language': 'en'},
        {'page': 'content', 'language': 'fr'},
    ])
)
@settings(max_examples=5, deadline=1000)
def test_language_selector_template_loads_required_tags(page_context):
    """
    Property 1: Bug Condition - Template Renders Successfully

    **Validates: Requirements 2.1, 2.2, 2.3**

    For any template render request where the structa/core language_selector.html template
    is included, the fixed template SHALL load the wagtail_i18n_tags library and successfully
    execute the get_translation tag without raising a TemplateSyntaxError.

    This property-based test generates different page contexts (homepage, content pages,
    different languages) to verify that the template would work correctly across all scenarios.

    EXPECTED ON UNFIXED CODE: Test FAILS
    - wagtail_i18n_tags is NOT in load statement
    - Template uses get_translation tag
    - Would raise TemplateSyntaxError when rendered

    EXPECTED ON FIXED CODE: Test PASSES
    - wagtail_i18n_tags IS in load statement
    - Template can successfully use get_translation tag
    - Template renders successfully with HTTP 200
    """
    has_tags, uses_get_translation, line_numbers = check_template_has_required_tags()

    # Assert: If template uses get_translation, it must load wagtail_i18n_tags
    if uses_get_translation:
        assert has_tags, (
            f"Template uses 'get_translation' tag on lines {line_numbers} "
            f"but does not load 'wagtail_i18n_tags' library. "
            f"This will cause TemplateSyntaxError when rendering pages with "
            f"language selector in context: {page_context}. "
            f"Expected: Line 1 should contain 'wagtail_i18n_tags' in load statement."
        )


def test_template_file_has_wagtail_i18n_tags():
    """
    Unit test: Verify the template file has wagtail_i18n_tags in load statement.

    **Validates: Requirements 2.2**

    EXPECTED ON UNFIXED CODE: FAILS (wagtail_i18n_tags missing)
    EXPECTED ON FIXED CODE: PASSES (wagtail_i18n_tags present)
    """
    has_tags, uses_get_translation, line_numbers = check_template_has_required_tags()

    template_path = 'assets/templates/partials/language_selector.html'

    with open(template_path, 'r') as f:
        first_line = f.readline()

    assert has_tags, (
        f"Line 1 of {template_path} should contain 'wagtail_i18n_tags' in the load statement. "
        f"Found: {first_line.strip()}. "
        f"The template uses 'get_translation' on lines {line_numbers}, which requires wagtail_i18n_tags."
    )


if __name__ == '__main__':
    """
    Run the bug exploration test directly.
    This will show the bug exists on unfixed code.
    """
    print("=" * 70)
    print("BUG CONDITION EXPLORATION - PROPERTY-BASED TEST")
    print("=" * 70)
    print()

    # Run the unit test
    print("Running unit test: test_template_file_has_wagtail_i18n_tags")
    print("-" * 70)
    try:
        test_template_file_has_wagtail_i18n_tags()
        print("✓ PASS: Template has wagtail_i18n_tags (bug is fixed)")
    except AssertionError as e:
        print(f"✗ FAIL: {e}")
        print()
        print("This is EXPECTED on unfixed code - the bug exists!")
    print()

    # Run the property-based test
    print("Running property-based test: test_language_selector_template_loads_required_tags")
    print("-" * 70)
    try:
        test_language_selector_template_loads_required_tags()
        print("✓ PASS: All generated test cases passed (bug is fixed)")
    except AssertionError as e:
        print(f"✗ FAIL: Property test failed")
        print(f"Counterexample: {e}")
        print()
        print("This is EXPECTED on unfixed code - the bug exists!")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Bug exploration complete. The test failures above confirm the bug exists.")
    print("After implementing the fix, these tests should PASS.")
