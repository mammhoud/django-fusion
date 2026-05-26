# Bugfix Requirements Document

**Category Context: Bug Fixes**
- **Category**: Fixes
- **Scope**: Bug fixes, error corrections, problem resolutions, patch implementations
- **Related Specs**: alliance-website-docker-fix, fix-get-translation-template-tag, fix-wagtailsnippets-assets-email-enhancement
- **Common Patterns**: Docker fixes, template issues, email system problems, asset management
- **Avoid Duplicates**: Check existing fixes specs before creating new bug fix specs


## Introduction

The Django application crashes with an Internal Server Error 500 when accessing the homepage due to an unregistered template tag `get_translation` in the `language_selector.html` template. The error occurs because the `wagtail_i18n_tags` template library, which provides the `get_translation` tag, is not loaded in the structa/core project's language selector template, while it is correctly loaded in the ctc-research project.

This bugfix will resolve the template syntax error by ensuring the required template tag library is loaded in all affected templates.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the homepage is accessed THEN the system crashes with TemplateSyntaxError: "Invalid block tag on line 25: 'get_translation', expected 'elif', 'else' or 'endif'. Did you forget to register or load this tag?"

1.2 WHEN the `structa/core/assets/templates/partials/language_selector.html` template is rendered THEN the system fails because `wagtail_i18n_tags` is not loaded in the template's load statement

1.3 WHEN any page using the language selector partial in structa/core is accessed THEN the system returns HTTP 500 error instead of rendering the page

### Expected Behavior (Correct)

2.1 WHEN the homepage is accessed THEN the system SHALL render the page successfully without template syntax errors

2.2 WHEN the `structa/core/assets/templates/partials/language_selector.html` template is rendered THEN the system SHALL successfully use the `get_translation` tag because `wagtail_i18n_tags` is loaded

2.3 WHEN any page using the language selector partial in structa/core is accessed THEN the system SHALL return HTTP 200 and display the page with functional language selection

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the ctc-research project's language selector is rendered THEN the system SHALL CONTINUE TO work correctly as it already has `wagtail_i18n_tags` loaded

3.2 WHEN language switching functionality is used THEN the system SHALL CONTINUE TO switch languages correctly using the existing form submission mechanism

3.3 WHEN the `get_language_info` tag is used in templates THEN the system SHALL CONTINUE TO display current language information correctly

3.4 WHEN flag icons are displayed for different languages THEN the system SHALL CONTINUE TO render the correct flag images based on language codes

3.5 WHEN translated page URLs are generated using `trans_page.url` THEN the system SHALL CONTINUE TO navigate to the correct translated version of pages
