# Bug Condition Exploration Test Results

## Task 1: Write Bug Condition Exploration Test

**Status:** ✓ COMPLETED

**Date:** 2024

**Test File:** `structa/core/core/CI/tests/test_language_selector_bug_exploration.py`

## Test Execution Summary

The bug condition exploration test was successfully written and executed on **UNFIXED CODE**. The test **FAILED as expected**, confirming that the bug exists.

## Counterexamples Found

### 1. Missing Template Tag Library

**Finding:** The `structa/core/assets/templates/partials/language_selector.html` template is missing `wagtail_i18n_tags` in its load statement.

**Evidence:**
- Line 1 content: `{% load static i18n wagtailcore_tags wagtailimages_tags wagtailsettings_tags %}`
- Missing: `wagtail_i18n_tags`

### 2. Unregistered Tag Usage

**Finding:** The template uses the `get_translation` tag without loading the required library.

**Evidence:**
- `get_translation` tag is used on lines: **25** and **27**
- The tag is provided by `wagtail_i18n_tags` library
- The library is NOT loaded in the template

### 3. Expected Runtime Error

**Finding:** When this template is rendered, Django will raise a `TemplateSyntaxError`.

**Expected Error Message:**
```
TemplateSyntaxError: Invalid block tag on line 25: 'get_translation',
expected 'elif', 'else' or 'endif'. Did you forget to register or load this tag?
```

**Impact:**
- HTTP 500 Internal Server Error when accessing pages that include this template
- Homepage and other pages using the language selector will crash
- Users cannot access the site

## Property-Based Test Results

### Test: `test_language_selector_template_loads_required_tags`

**Property Tested:** For any template render request where the structa/core language_selector.html template is included, the template SHALL load the wagtail_i18n_tags library.

**Test Strategy:** Generated 5 different page contexts (homepage, content pages, different languages: en, ar, es, fr) to verify the template would work correctly across all scenarios.

**Result on Unfixed Code:** ✗ FAILED (Expected)

**Counterexample:**
```
Template uses 'get_translation' tag on lines [25, 27] but does not load
'wagtail_i18n_tags' library. This will cause TemplateSyntaxError when
rendering pages with language selector in context:
{'page': 'homepage', 'language': 'en'}
```

**Validation:** This test validates Requirements 2.1, 2.2, 2.3

### Test: `test_template_file_has_wagtail_i18n_tags`

**Test Type:** Unit test

**Result on Unfixed Code:** ✗ FAILED (Expected)

**Error Message:**
```
Line 1 of assets/templates/partials/language_selector.html should contain
'wagtail_i18n_tags' in the load statement.
Found: {% load static i18n wagtailcore_tags wagtailimages_tags wagtailsettings_tags %}.
The template uses 'get_translation' on lines [25, 27], which requires wagtail_i18n_tags.
```

**Validation:** This test validates Requirement 2.2

## Root Cause Confirmation

The bug exploration test confirms the hypothesized root cause from the design document:

1. ✓ **Missing Template Library Load**: The `structa/core/assets/templates/partials/language_selector.html` template does NOT include `wagtail_i18n_tags` in the load statement on line 1

2. ✓ **Tag Usage Without Registration**: The template uses `get_translation` tag on lines 25 and 27 without loading the required library

3. ✓ **Copy-Paste Inconsistency**: The ctc-research project has the correct load statement, but the structa/core template is missing it

## Expected Behavior After Fix

After implementing the fix (adding `wagtail_i18n_tags` to line 1), these tests should:

- ✓ **PASS** - Template will have the required library loaded
- ✓ **PASS** - Property-based test will succeed for all generated contexts
- ✓ **PASS** - Homepage and other pages will render successfully with HTTP 200
- ✓ **PASS** - No TemplateSyntaxError will occur

## Test Files Created

1. **Property-Based Test:** `structa/core/core/CI/tests/test_language_selector_bug_exploration.py`
   - Contains property-based test using Hypothesis
   - Generates multiple test cases across different page contexts
   - Validates Requirements 2.1, 2.2, 2.3

2. **Simple Verification Script:** `structa/core/test_bug_simple.py`
   - Standalone script for quick verification
   - Can be run without Django setup
   - Useful for manual testing

## How to Run Tests

### Property-Based Test
```bash
cd structa/core
uv run python core/CI/tests/test_language_selector_bug_exploration.py
```

### Simple Verification
```bash
cd structa/core
uv run python test_bug_simple.py
```

## Conclusion

✓ **Bug Confirmed:** The exploration test successfully confirmed that the bug exists in the unfixed code.

✓ **Counterexamples Documented:** Multiple counterexamples were found and documented, proving the bug condition.

✓ **Test Ready for Validation:** The same test will be used to verify the fix in Task 3.2, where it should PASS after the fix is implemented.

✓ **Requirements Validated:** The test validates Requirements 2.1, 2.2, and 2.3 from the bugfix specification.

---

**Next Steps:** Proceed to Task 2 (Write preservation property tests) and then Task 3 (Implement the fix).
