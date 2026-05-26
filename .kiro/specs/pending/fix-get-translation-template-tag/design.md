# Fix get_translation Template Tag Bugfix Design

**Category Context: Bug Fixes**
- **Category**: Fixes
- **Scope**: Bug fixes, error corrections, problem resolutions, patch implementations
- **Related Specs**: alliance-website-docker-fix, fix-get-translation-template-tag, fix-wagtailsnippets-assets-email-enhancement
- **Common Patterns**: Docker fixes, template issues, email system problems, asset management
- **Avoid Duplicates**: Check existing fixes specs before creating new bug fix specs


## Overview

This bugfix addresses a TemplateSyntaxError that causes the Django application to crash with HTTP 500 when accessing the homepage. The bug occurs because the `structa/core/assets/templates/partials/language_selector.html` template uses the `get_translation` tag without loading the `wagtail_i18n_tags` library that provides it. The fix is minimal and surgical: add `wagtail_i18n_tags` to the existing load statement on line 1 of the template.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when the language_selector.html template in structa/core is rendered
- **Property (P)**: The desired behavior - the template renders successfully with the `get_translation` tag working correctly
- **Preservation**: All existing functionality (language switching, flag display, current language info) that must remain unchanged
- **get_translation**: A template tag from wagtail_i18n_tags that retrieves translated versions of pages
- **wagtail_i18n_tags**: The Django template tag library that provides internationalization utilities for Wagtail CMS

## Bug Details

### Bug Condition

The bug manifests when the `structa/core/assets/templates/partials/language_selector.html` template is rendered. The template uses the `get_translation` tag on lines 25 and 27, but the `wagtail_i18n_tags` library is not loaded in the template's load statement on line 1.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type TemplateRenderContext
  OUTPUT: boolean

  RETURN input.template_path == 'structa/core/assets/templates/partials/language_selector.html'
         AND 'wagtail_i18n_tags' NOT IN input.loaded_libraries
         AND template_uses_tag(input, 'get_translation')
END FUNCTION
```

### Examples

- **Example 1**: User accesses homepage → language_selector.html is included → TemplateSyntaxError on line 25: "Invalid block tag: 'get_translation'"
- **Example 2**: User navigates to any page using the language selector partial → HTTP 500 error instead of page rendering
- **Example 3**: Template attempts to execute `{% get_translation page lang.code as trans_page %}` → Django cannot find the tag because wagtail_i18n_tags is not loaded
- **Edge Case**: The ctc-research project's language_selector.html works correctly because it has `wagtail_i18n_tags` in its load statement

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Language switching functionality via form submission must continue to work exactly as before
- Flag icon display for different languages must remain unchanged
- Current language display using `get_language_info` tag must continue to work
- Translated page URL navigation using `trans_page.url` must continue to function correctly
- All other loaded template libraries (static, i18n, wagtailcore_tags, wagtailimages_tags, wagtailsettings_tags) must continue to work

**Scope:**
All inputs that do NOT involve rendering the structa/core language_selector.html template should be completely unaffected by this fix. This includes:
- The ctc-research project's language selector (already working)
- Any other templates in the application
- Backend language switching logic
- Database queries for translated pages

## Hypothesized Root Cause

Based on the bug description and code analysis, the root cause is clear and straightforward:

1. **Missing Template Library Load**: The `structa/core/assets/templates/partials/language_selector.html` template was created without including `wagtail_i18n_tags` in the load statement on line 1
   - Current load statement: `{% load static i18n wagtailcore_tags wagtailimages_tags wagtailsettings_tags %}`
   - Required load statement: `{% load static i18n wagtailcore_tags wagtailimages_tags wagtailsettings_tags wagtail_i18n_tags %}`

2. **Copy-Paste Inconsistency**: The ctc-research project has the correct load statement, but when the structa/core template was created, `wagtail_i18n_tags` was omitted

3. **No Runtime Detection**: Django's template system only validates tags at render time, so the error wasn't caught until the template was actually used

## Correctness Properties

Property 1: Bug Condition - Template Renders Successfully

_For any_ template render request where the structa/core language_selector.html template is included, the fixed template SHALL load the wagtail_i18n_tags library and successfully execute the get_translation tag without raising a TemplateSyntaxError, allowing the page to render with HTTP 200.

**Validates: Requirements 2.1, 2.2, 2.3**

Property 2: Preservation - Existing Functionality Unchanged

_For any_ template render request that does NOT involve the structa/core language_selector.html template, OR for any functionality within the language selector that does not depend on the get_translation tag, the fixed code SHALL produce exactly the same behavior as the original code, preserving language switching, flag display, and current language information display.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

## Fix Implementation

### Changes Required

The fix is minimal and surgical - only one line needs to be modified.

**File**: `structa/core/assets/templates/partials/language_selector.html`

**Line**: 1

**Specific Changes**:
1. **Add wagtail_i18n_tags to Load Statement**: Append `wagtail_i18n_tags` to the existing load statement
   - Current: `{% load static i18n wagtailcore_tags wagtailimages_tags wagtailsettings_tags %}`
   - Fixed: `{% load static i18n wagtailcore_tags wagtailimages_tags wagtailsettings_tags wagtail_i18n_tags %}`
   - This matches the working implementation in ctc-research/assets/templates/partials/language_selector.html

**No other changes are required** - the rest of the template is correct and functional.

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, confirm the bug exists on unfixed code by attempting to render the template, then verify the fix works correctly and preserves all existing functionality.

### Exploratory Bug Condition Checking

**Goal**: Surface the TemplateSyntaxError that demonstrates the bug BEFORE implementing the fix. Confirm the root cause is the missing wagtail_i18n_tags load statement.

**Test Plan**: Attempt to access the homepage or any page that includes the language_selector.html partial. Observe the TemplateSyntaxError in the Django error page or logs. Verify the error message mentions 'get_translation' tag not being registered.

**Test Cases**:
1. **Homepage Access Test**: Access the homepage URL (will fail with HTTP 500 on unfixed code)
2. **Error Message Verification**: Confirm error message is "Invalid block tag on line 25: 'get_translation'" (will show on unfixed code)
3. **Template Line Inspection**: Verify line 1 of structa/core language_selector.html does NOT contain wagtail_i18n_tags (will be missing on unfixed code)
4. **Comparison Test**: Verify ctc-research language_selector.html line 1 DOES contain wagtail_i18n_tags (should pass on unfixed code)

**Expected Counterexamples**:
- TemplateSyntaxError: "Invalid block tag on line 25: 'get_translation', expected 'elif', 'else' or 'endif'. Did you forget to register or load this tag?"
- HTTP 500 Internal Server Error when accessing pages with language selector
- Root cause confirmed: wagtail_i18n_tags is missing from load statement

### Fix Checking

**Goal**: Verify that after adding wagtail_i18n_tags to the load statement, the template renders successfully without errors.

**Pseudocode:**
```
FOR ALL page_request WHERE includes_language_selector(page_request, 'structa/core') DO
  response := render_page_with_fixed_template(page_request)
  ASSERT response.status_code == 200
  ASSERT 'TemplateSyntaxError' NOT IN response.content
  ASSERT language_selector_is_rendered(response)
END FOR
```

### Preservation Checking

**Goal**: Verify that all existing functionality continues to work exactly as before the fix.

**Pseudocode:**
```
FOR ALL functionality WHERE NOT directly_related_to_get_translation_tag(functionality) DO
  ASSERT behavior_after_fix(functionality) == behavior_before_fix(functionality)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across different page types and language combinations
- It catches edge cases that manual unit tests might miss (e.g., pages without translations, invalid language codes)
- It provides strong guarantees that behavior is unchanged for all non-buggy scenarios

**Test Plan**: Manually test existing functionality on UNFIXED code first to document current behavior, then verify the same behavior persists after the fix.

**Test Cases**:
1. **Language Switching Preservation**: Click language dropdown, select different language, verify form submission works and language changes
2. **Flag Display Preservation**: Verify flag icons display correctly for all configured languages (en, ar, es, etc.)
3. **Current Language Indicator Preservation**: Verify checkmark appears next to currently selected language
4. **CTC-Research Preservation**: Verify ctc-research language selector continues to work without any changes
5. **Translated URL Navigation**: For pages with translations, verify clicking language link navigates to correct translated page

### Unit Tests

- Test that homepage renders successfully with HTTP 200 status code
- Test that language_selector.html partial renders without TemplateSyntaxError
- Test that get_translation tag successfully retrieves translated page objects
- Test edge case: pages without translations fall back to language URL correctly

### Property-Based Tests

- Generate random page objects with various translation states and verify language selector renders for all
- Generate random language code combinations and verify flag display works correctly
- Test that language switching works across many different page types and contexts

### Integration Tests

- Test full user flow: access homepage → open language dropdown → see all languages with flags → click language → navigate to translated page
- Test language selector in different page contexts (homepage, content pages, admin pages if applicable)
- Test that visual feedback (checkmark, active state) appears correctly after language selection
