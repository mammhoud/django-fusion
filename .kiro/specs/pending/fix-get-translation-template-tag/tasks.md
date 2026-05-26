# Implementation Plan

**Category Context: Bug Fixes**
- **Category**: Fixes
- **Scope**: Bug fixes, error corrections, problem resolutions, patch implementations
- **Related Specs**: alliance-website-docker-fix, fix-get-translation-template-tag, fix-wagtailsnippets-assets-email-enhancement
- **Common Patterns**: Docker fixes, template issues, email system problems, asset management
- **Avoid Duplicates**: Check existing fixes specs before creating new bug fix specs


- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Template Renders Successfully
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Scope the property to the concrete failing case - accessing homepage or any page that includes structa/core language_selector.html
  - Test that rendering structa/core/assets/templates/partials/language_selector.html raises TemplateSyntaxError for 'get_translation' tag
  - Test that the error message mentions 'get_translation' tag not being registered
  - Test that line 1 of the template does NOT contain 'wagtail_i18n_tags' in the load statement
  - The test assertions should match: template renders successfully with HTTP 200, no TemplateSyntaxError, language selector is rendered
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found: TemplateSyntaxError on line 25, HTTP 500 errors, missing wagtail_i18n_tags in load statement
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Existing Functionality Unchanged
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (ctc-research language selector, other templates)
  - Write property-based tests capturing observed behavior patterns:
    - Language switching via form submission works correctly
    - Flag icons display for all configured languages
    - Current language indicator (checkmark) appears correctly
    - Other loaded template libraries (static, i18n, wagtailcore_tags, wagtailimages_tags, wagtailsettings_tags) continue to work
    - ctc-research language selector continues to work without changes
  - Property-based testing generates many test cases for stronger guarantees across different page types and language combinations
  - Run tests on UNFIXED code (test against ctc-research or other working templates)
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Fix for missing wagtail_i18n_tags template library

  - [x] 3.1 Implement the fix
    - Modify line 1 of structa/core/assets/templates/partials/language_selector.html
    - Add 'wagtail_i18n_tags' to the existing load statement
    - Change from: `{% load static i18n wagtailcore_tags wagtailimages_tags wagtailsettings_tags %}`
    - Change to: `{% load static i18n wagtailcore_tags wagtailimages_tags wagtailsettings_tags wagtail_i18n_tags %}`
    - This matches the working implementation in ctc-research/assets/templates/partials/language_selector.html
    - _Bug_Condition: isBugCondition(input) where input.template_path == 'structa/core/assets/templates/partials/language_selector.html' AND 'wagtail_i18n_tags' NOT IN input.loaded_libraries AND template_uses_tag(input, 'get_translation')_
    - _Expected_Behavior: Template renders successfully with HTTP 200, no TemplateSyntaxError, get_translation tag executes correctly_
    - _Preservation: Language switching, flag display, current language info, other template libraries, ctc-research language selector all continue to work unchanged_
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Template Renders Successfully
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - Verify homepage renders with HTTP 200
    - Verify no TemplateSyntaxError occurs
    - Verify language selector renders correctly with get_translation tag working
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Existing Functionality Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm language switching still works
    - Confirm flag display still works
    - Confirm current language indicator still works
    - Confirm ctc-research language selector still works
    - Confirm all other template libraries still work

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
